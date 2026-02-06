from .policy import PartnerPolicy
from .file_provider import InMemoryPolicyProvider

POLICY_PROVIDER = InMemoryPolicyProvider(
    policies={
        "nav": PartnerPolicy("nav", frozenset({"Leads", "tokens"})),
        "intuit": PartnerPolicy("intuit", frozenset({"Leads"})),
    }
)
