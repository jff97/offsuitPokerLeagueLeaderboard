
from typing import Dict, List

from offsuit_analyzer.the_wheel import wheel_qualification_service


def get_wheel_qualifiers_by_bar() -> Dict[str, List[str]]:
    return wheel_qualification_service.get_wheel_qualifiers_by_bar()
