from __future__ import annotations

import inspect


class BodySection:
    BODY = "Body"
    CARDIAC = "Cardiac"
    CHEST = "Chest"
    MAMMO = "Mammo"
    MSK = "MSK"
    NEURO = "Neuro"
    NUCMED = "Nuc Med"
    PET = "PET"
    PEDS = "PEDS"

    @classmethod
    def get_section(cls, text: str) -> str:
        """Given a string, returns the body section it belongs to.

        Args:
            text: String that could contain a body section.

        Returns:
            Either the body section or an empty string if no body section was found.

        """
        members = {x[0]:x[1] for x in inspect.getmembers(cls)
                   if not x[0].startswith("__") and not inspect.ismethod(x[1])}
        for k, v in members.items():
            if v.lower() in text.lower():
                return v

        return ""

