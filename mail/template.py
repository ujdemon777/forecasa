verification_link = "https://example.com/verify?token=your_verification_token"

# Construct the HTML email message with the verification link
message = f"""
<html>
<head></head>
<body>
    <p>Dear user,</p>
    <p>Thank you for signing up. Please click the following link to verify your email:</p>
    <a href="{verification_link}">Verify Email</a>
    <p>If the link doesn't work, copy and paste the following URL into your browser:</p>
    <p>{verification_link}</p>
</body>
</html>
"""