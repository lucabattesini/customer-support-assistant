from app.domain.enums import PolicySectionKey
from app.domain.errors import PolicySectionUnavailableError
from app.domain.models import PolicySection
from app.repositories.policy_repository import PolicyRepository


class PolicyService:
    """Access to the store policy sections."""

    def __init__(self, policies: PolicyRepository) -> None:
        self._policies = policies

    def get(self, section: PolicySectionKey) -> PolicySection:
        """Return a policy section.

        Raises:
            PolicySectionUnavailableError: When the section has no content stored.
        """
        policy = self._policies.get_section(section)
        if policy is None:
            raise PolicySectionUnavailableError({"section": section.value})
        return policy
