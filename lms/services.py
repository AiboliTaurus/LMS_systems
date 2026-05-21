import stripe
from django.conf import settings


class StripeService:
    """
    Сервис для работы с платежной системой Stripe
    """

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_product(self, name, description=None):
        """
        Создание продукта в Stripe
        Документация: https://stripe.com/docs/api/products/create
        """
        try:
            product = stripe.Product.create(
                name=name,
                description=description or "",
                metadata={'integration_type': 'lms_platform'}
            )
            return {
                'success': True,
                'product_id': product.id,
                'product': product
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_price(self, product_id, amount, currency='rub'):
        """
        Создание цены для продукта в Stripe
        Документация: https://stripe.com/docs/api/prices/create
        Внимание: сумма указывается в КОПЕЙКАХ!
        """
        try:
            # Конвертируем рубли в копейки (умножаем на 100)
            amount_in_cents = int(amount * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency=currency,
                metadata={'platform': 'lms'}
            )
            return {
                'success': True,
                'price_id': price.id,
                'price': price
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_checkout_session(self, price_id, success_url, cancel_url, user_email=None):
        """
        Создание сессии для оплаты
        Документация: https://stripe.com/docs/api/checkout/sessions/create
        """
        try:
            session_data = {
                'payment_method_types': ['card'],
                'line_items': [{
                    'price': price_id,
                    'quantity': 1,
                }],
                'mode': 'payment',
                'success_url': success_url,
                'cancel_url': cancel_url,
            }

            if user_email:
                session_data['customer_email'] = user_email

            session = stripe.checkout.Session.create(**session_data)

            return {
                'success': True,
                'session_id': session.id,
                'session_url': session.url,
                'session': session
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_session_status(self, session_id):
        """
        Получение статуса сессии оплаты
        Документация: https://stripe.com/docs/api/checkout/sessions/retrieve

        Возможные статусы:
        - 'open': Сессия активна, ждет оплаты
        - 'complete': Сессия завершена, оплата прошла
        - 'expired': Сессия истекла

        payment_status может быть:
        - 'unpaid': Не оплачено
        - 'paid': Оплачено
        - 'no_payment_required': Оплата не требуется
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            # Маппинг статусов для нашей модели
            if session.payment_status == 'paid':
                status = 'paid'
            elif session.status == 'expired':
                status = 'failed'
            elif session.status == 'open' and session.payment_status == 'unpaid':
                status = 'pending'
            else:
                status = 'pending'

            return {
                'success': True,
                'status': status,
                'payment_status': session.payment_status,
                'session_status': session.status,
                'payment_intent_id': session.payment_intent,
                'customer_email': session.customer_details.email if session.customer_details else None,
                'amount_total': session.amount_total / 100 if session.amount_total else 0,
                'currency': session.currency,
                'session': session
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_test_cards_info(self):
        """
        Возвращает информацию о тестовых картах Stripe
        Для документации и тестирования
        """
        return {
            'visa': '4242424242424242',
            'visa_debit': '4000056655665556',
            'mastercard': '5555555555554444',
            'mastercard_debit': '5200828282828210',
            'mastercard_prepaid': '5105105105105100',
            'amex': '378282246310005',
            'discover': '6011111111111117',
            'diners': '3056930009020004',
            'jcb': '3566002020360505',
            'unionpay': '6200000000000005'
        }


def create_payment_session(payment):
    """
    Создание платежной сессии для существующего платежа
    """
    service = StripeService()

    # Определяем название и описание продукта
    if payment.course:
        product_name = f"Курс: {payment.course.title}"
        product_description = payment.course.description or ""
    elif payment.lesson:
        product_name = f"Урок: {payment.lesson.title}"
        product_description = payment.lesson.description or ""
    else:
        product_name = f"Платеж #{payment.id}"
        product_description = "Оплата в LMS системе"

    # Создаём продукт
    product_result = service.create_product(product_name, product_description)
    if not product_result['success']:
        return product_result

    # Создаём цену (сумма в рублях, Stripe сконвертирует в копейки)
    price_result = service.create_price(product_result['product_id'], float(payment.amount))
    if not price_result['success']:
        return price_result

    # Создаём сессию оплаты
    base_url = "http://localhost:8000"  # В продакшене заменить на реальный домен
    success_url = f"{base_url}/api/payments/{payment.id}/success/"
    cancel_url = f"{base_url}/api/payments/{payment.id}/cancel/"

    session_result = service.create_checkout_session(
        price_id=price_result['price_id'],
        success_url=success_url,
        cancel_url=cancel_url,
        user_email=payment.user.email
    )

    if not session_result['success']:
        return session_result

    # Обновляем платеж с данными от Stripe
    payment.stripe_product_id = product_result['product_id']
    payment.stripe_price_id = price_result['price_id']
    payment.stripe_session_id = session_result['session_id']
    payment.payment_url = session_result['session_url']
    payment.payment_method = 'card'
    payment.save()

    return {
        'success': True,
        'payment_url': session_result['session_url'],
        'session_id': session_result['session_id']
    }


def get_payment_status_from_stripe(session_id):
    """
    Получение статуса платежа из Stripe по ID сессии
    """
    service = StripeService()
    return service.get_session_status(session_id)
