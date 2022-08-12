import warnings
import re
from functools import lru_cache


class Report:
    """Class that handles a radiology report.

    Attributes:
        text: The text of the report.
        gt_pathology: The pathology assigned to this report by a medical expert.

    """
    headers = ["examination", "clinical indication", "history", "technique", "comparison", "electronic signature"]
    impression_token = "impression:"
    electronic_signature_token = "electronic signature"

    def __init__(self, text: str, gt_pathology: str | None = None) -> None:
        """Initializes a Report object."""
        self.text = text.lower()
        self.gt_pathology = gt_pathology.lower() if gt_pathology is not None else None

        # This will be assigned later by a non-human model
        self.pred_pathology = None

    def is_prediction_right(self) -> bool | None:
        """Checks whether the predicted pathology is the same as the ground truth."""
        if self.gt_pathology is None:
            warnings.warn("Ground truth pathology has not been assigned. Cannot check if prediction is right.")
            return None

        if self.pred_pathology is None:
            warnings.warn("Predicted pathology has not been assigned. Cannot check if prediction is right.")
            return None

        return self.pred_pathology.lower() == self.gt_pathology.lower()

    def has_impression(self) -> bool:
        """Check whether a report has an impression section or not."""
        if self.impression_token in self.text:
            return True

        return False

    def has_electronic_signature(self) -> bool:
        """Check whether a report has an electronic signature section or not."""
        if self.electronic_signature_token in self.text:
            return True

        return False

    def get_impression(self) -> str:
        """Returns the impression section of the report."""
        if not self.has_impression():
            warnings.warn("This report has no impression section.")
            return ""

        words_list = []
        is_impression = False
        for token in self.text.split():
            # Check for end of section and break
            if any(x in token for x in self.headers):
                break

            if is_impression:
                words_list.append(token)

            # Find start of section
            if self.impression_token in token:
                is_impression = True

        return " ".join(words_list)

    def get_electronic_signature(self) -> str:
        """Returns the electronic signature section of the report."""
        if not self.has_electronic_signature():
            warnings.warn("This report has no electronic signature section.")
            return ""

        # We assume that the electronic signature is the last section of the report
        words_list = []
        is_electronic_signature = False
        for bigram in self.get_bigrams(self.text):
            if is_electronic_signature:
                # Append only second token of brigram to not create duplication
                words_list.append(bigram.split()[1])

            # Find start of section
            if self.electronic_signature_token in bigram:
                is_electronic_signature = True

        return " ".join(words_list)

    @lru_cache()
    def get_authors(self):
        """Gets the doctors that dictated and signed the report.

        They can be the same person.

        Returns:

        """
        electronic_signature = self.get_electronic_signature()

        # Case 1: same author
        if "dictated by and signed by" in electronic_signature:
            dictator = signer = re.search(r'signed by(.*?)\d', electronic_signature).group(1).strip()
        else:
            dictator = re.search(r'dictated by(.*?)and signed by', electronic_signature).group(1).strip()
            signer = re.search(r'signed by(.*?)\d', electronic_signature).group(1).strip()

        return dictator, signer

    def get_dictator(self):
        """Gets the doctor that dictated the report.

        Returns:
            The name of the doctor.

        """
        return self.get_authors()[0]

    def get_signer(self):
        """Gets the doctor that signed the report.

        Returns:
            The name of the doctor.

        """
        return self.get_authors()[1]

    @staticmethod
    def get_bigrams(s: str) -> list[str]:
        """Gets all the bigrams in a string."""
        # Zip the input string except the last element and the input string except the first element and join the
        # resulting tuple into a string
        return [" ".join(x) for x in zip(s.split()[:-1], s.split()[1:])]


if __name__ == '__main__':
    report_text = 'Findings/IMPRESSION: The patellofemoral view shows normal articular congruence, absence of joint ' \
                  'space narrowing, no evidence of osteophytosis at the medial and lateral margins of the ' \
                  'patellofemoral compartment. History: Knee pain Technique:XR KNEE 1 VIEW SPECIAL RIGHT Comparison: ' \
                  'AP and lateral Knee radiograph 12/2/2019 Electronic Signature: I personally reviewed the images ' \
                  'and agree with this report. Final Report: Dictated by and Signed by Attending Mitchell Kline MD ' \
                  '12/18/2019 7:33 AM'

    report_text = 'Please note there is considerable air in the impression. There is a fracture ' \
                  'of the LATERAL malleolus, not the medial malleolus. This exam was discussed ' \
                  'by Dr. Riviello with Fares on 12/20/2019 at 10:32 PM with readback verification. ' \
                  'Electronic Signature: I personally reviewed the images and agree with this ' \
                  'report. Final Report: Dictated by and Signed by Attending Peter Riviello MD ' \
                  '12/20/2019 10:32 PM *******END OF ADDENDUM****** IMPRESSION: There is a minimally displaced ' \
                  'fracture of the left medial malleolus below the level of the ankle mortise, with a horizontal ' \
                  'orientation. The ankle mortise appears grossly congruent. No proximal leg ' \
                  'fracture is seen. The alignment is near-anatomic. There is a small ankle ' \
                  'joint effusion and soft tissue swelling around the ankle. There is a ' \
                  'benign-appearing chondroid type lesion within the distal tibia likely ' \
                  'representing an enchondroma. History: Trauma, left ankle pain. ' \
                  'Technique: XR TIBIA FIBULA AP AND LATERAL LEFT, XR ANKLE AP LATERAL AND ' \
                  'OBLIQUE LEFT, XR FOOT AP LATERAL AND OBLIQUE LEFT Comparison: None ' \
                  'Electronic Signature: I personally reviewed the images and agree with this ' \
                  'report. Final Report: Dictated by and Signed by Attending Peter Riviello MD 12/20/2019 10:20 PM'

    report = Report(report_text)
    report.get_impression()
    report.is_prediction_right()
    report.get_electronic_signature()
    report.get_authors()
    report.get_dictator()
    report.get_signer()
