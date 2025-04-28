from django.core.mail import send_mail
from django.conf import settings
from Accommodation.models import Reservation
"""
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'accommodation@example.com'
"""

class EmailNotificationService:
    @staticmethod
    def notify_specialist_reservation_created(reservation):
        """
        Send email notification to specialist when a new reservation is created.
        """
        specialist = reservation.manager
        subject = f"New Reservation Notification: {reservation.house_id.name}"
        message = (
            f"Student {reservation.student.name} has made a reservation for {reservation.house_id.name}, "
            f"from {reservation.period_from} to {reservation.period_to}."
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [specialist.email],
            fail_silently=False,
        )
    
    @staticmethod
    def notify_specialist_reservation_cancelled(reservation):
        """
        Send email notification to specialist when a reservation is cancelled.
        """
        specialist = reservation.manager
        subject = f"Reservation Cancelled Notification: {reservation.house_id.name}"
        message = (
            f"Student {reservation.student.name} has cancelled their reservation for {reservation.house_id.name}, "
            f"which was scheduled from {reservation.period_from} to {reservation.period_to}."
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [specialist.email],
            fail_silently=False,
        )
    
    @staticmethod
    def notify_student_reservation_cancelled(reservation):
        """
        Send email notification to student when a specialist cancels their reservation.
        """
        student = reservation.student
        house = reservation.house_id
        subject = f"Your Reservation for {house.name} has been Cancelled"
        message = (
            f"Dear {student.name},\n\n"
            f"Your reservation for {house.name} from {reservation.period_from} to {reservation.period_to} "
            f"has been cancelled by specialist {reservation.manager.name}.\n\n"
            f"Please contact the specialist for more information or make a new reservation."
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False,
        )
    @staticmethod
    def notify_student_reservation_confirmed(reservation):
        """
        Send email notification to student when a specialist confirms their reservation.
        """
        student = reservation.student
        house = reservation.house_id
        subject = f"Your Reservation for {house.name} has been Confirmed"
        message = (
            f"Dear {student.name},\n\n"
            f"Your reservation for {house.name} from {reservation.period_from} to {reservation.period_to} "
            f"has been confirmed by specialist {reservation.manager.name}.\n\n"
            f"If you have any questions, please contact the specialist directly."
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False,
        )