# Created at 10.09.22
from rest_framework.routers import DefaultRouter

from .views import (
    MerchantViewSet
)

router = DefaultRouter()

router.register("merchant", MerchantViewSet, basename="merchant")
