import json
from decimal import Decimal, InvalidOperation

from django.db import DatabaseError, IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Payment

EDITABLE_FIELDS = {"amount", "currency"}  

def error(message, status, **extra):
    return JsonResponse({"error": message, **extra}, status=status)


def serialize(p):
    return {
        "id": p.id,
        "reference": p.reference,
        "amount": str(p.amount),
        "currency": p.currency,
        "status": p.status,
        "created_at": p.created_at.isoformat(),
    }
def parse_json(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, error("Malformed JSON body", 400)
    if not isinstance(data, dict):
        return None, error("JSON body must be an object", 400)
    return data, None


def parse_amount(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("amount must be a number")
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        raise ValueError("amount must be a number")
    if not amount.is_finite() or amount <= 0:
        raise ValueError("amount must be greater than 0")
    if amount.as_tuple().exponent < -2:
        raise ValueError("amount can have at most 2 decimal places")
    return amount
    


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def payment_list(request):
    if request.method == "GET":
        payments = Payment.objects.all().order_by("-created_at")
        status = request.GET.get("status")
        if status:
            status = status.upper()
            if status not in Payment.Status.values:
                return error("Invalid status filter", 400, allowed=Payment.Status.values)
            payments = payments.filter(status=status)
        return JsonResponse({"payments": [serialize(p) for p in payments]})

    # POST
    data, err = parse_json(request)
    if err:
        return err

    errors = {}

    reference = data.get("reference")
    if not isinstance(reference, str) or not reference.strip():
        errors["reference"] = "required, non-empty string"

    amount = None
    if "amount" not in data:
        errors["amount"] = "required"
    else:
        try:
            amount = parse_amount(data["amount"])
        except ValueError as e:
            errors["amount"] = str(e)

    currency = data.get("currency")
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha():
        errors["currency"] = "required, 3-letter code such as KES"

    if "status" in data:
        errors["status"] = "cannot be set; new payments always start as PENDING"

    if errors:
        return error("Validation failed", 400, fields=errors)

    try:
        with transaction.atomic():
            payment = Payment.objects.create(
                reference=reference.strip(),
                amount=amount,
                currency=currency.upper(),
        ) 
    except IntegrityError:        
        return error("A payment with this reference already exists", 409)
    except DatabaseError:
        return error("Database error, please try again later", 500)

    return JsonResponse(serialize(payment), status=201)


@ensure_csrf_cookie
@require_http_methods(["GET", "PATCH"])
def payment_detail(request, pk):
    try:
        payment = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return error("Payment not found", 404)
    except DatabaseError:
        return error("Database error, please try again later", 500)

    if request.method == "GET":
        return JsonResponse(serialize(payment))

    # PATCH
    data, err = parse_json(request)
    if err:
        return err
    if not data:
        return error("No fields to update", 400)
    if "status" in data:
        return error("status cannot be changed through this endpoint", 400)

    unknown = set(data) - EDITABLE_FIELDS
    if unknown:
        return error("Fields not editable", 400, fields=sorted(unknown))

    errors = {}
    if "amount" in data:
        try:
            payment.amount = parse_amount(data["amount"])
        except ValueError as e:
            errors["amount"] = str(e)
    if "currency" in data:
        currency = data["currency"]
        if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha():
            errors["currency"] = "must be a 3-letter code such as KES"
        else:
            payment.currency = currency.upper()
    if errors:
        return error("Validation failed", 400, fields=errors)

    try:
        payment.save()
    except DatabaseError:
        return error("Database error, please try again later", 500)

    return JsonResponse(serialize(payment))