import base64
import logging
from typing import Optional

import requests
from app.core.security import SecurityManager
from app.core.settings import getSettings

logger = logging.getLogger(__name__)


class SMSService:
    """Simple SMS service for sending SMS to users."""

    def __init__(
        self,
        apiKey: Optional[str] = None,
        apiSecret: Optional[str] = None,
        senderId: str = "Vireakbo RC Store",
    ):
        """Initialize SMS service."""
        self.apiKey = apiKey or getSettings.TWILIO_ACCOUNT_SID
        self.apiSecret = apiSecret or getSettings.TWILIO_AUTH_TOKEN
        self.senderId = (
            senderId
            if senderId != "Vireakbo RC Store"
            else getSettings.TWILIO_PHONE_NUMBER
        )

    async def sendSms(self, phoneNumber: str, message: str) -> bool:
        """Send SMS to phone number using Twilio API."""

        phone = self._formatPhoneNumber(phoneNumber)
        if not self.apiKey:
            return True
        auth = base64.b64encode(f"{self.apiKey}:{self.apiSecret}".encode()).decode()
        response = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{self.apiKey}/Messages.json",
            data={"To": phone, "From": self.senderId, "Body": message},
            headers={"Authorization": f"Basic {auth}"},
        )
        return response.status_code == 201

    async def sendOtpSms(self, phoneNumber: str) -> str:
        """Generate and send OTP SMS to phone number."""
        otp = SecurityManager.generateOTP()
        message = f"Your Vireakbo RC Store verification code is: {otp}."

        smsSent = await self.sendSms(phoneNumber, message)
        return otp if smsSent else ""

    def _formatPhoneNumber(self, phoneNumber: str) -> str:
        """Format phone number for Cambodia (+855)."""
        cleanPhone = "".join(c for c in phoneNumber if c.isdigit() or c == "+")

        if cleanPhone.startswith("0"):
            return "+855" + cleanPhone[1:]
        elif not cleanPhone.startswith("+"):
            return "+855" + cleanPhone
        return cleanPhone


# Global SMS service instance
smsService = SMSService()
