from django.db import models


class Wallet(models.Model):
    public_address = models.CharField(max_length=255)
    private_key = models.CharField(max_length=255)
    currency = models.CharField(max_length=10)

    def __str__(self) -> str:
        return f'{self.currency}: {self.public_address}'
