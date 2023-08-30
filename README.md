# DeviceTimer
LNbits extension compatible with bitcoinSwitch device for timed triggering.

This extension behaves like the standard LNURLdevice extension with the following changes:

 - Payments available during specified time window. This allows to create a device (for instance animal feeding) with opening hours so that it is only accessible during a specific time window.
 - Timeout after each payment. After each succesful payment, the device is blocked for some time. This to prevent overfeeding or triggering when feeding is active.
 - When making a payment is not allowed, an alternative image is displayed instead of a QR code. The LNURL payment flow also returns an error when trying to make a payment outside opening hours.
 - Removed support for devices other that bitcoinSwitch

This LNbits extension was built with the support of <a href="https://www.business-bitcoin.de">Business Bitcoin</a>.



