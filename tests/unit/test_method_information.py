from __future__ import annotations

import unittest

from hook.method_analysis.method_information import MethodInformation


class MethodInformationTest(unittest.TestCase):
    """Verify that method metadata is stored correctly and remains immutable.

    These tests check that MethodInformation preserves the method name, sorting
    group, and original index provided at creation, and that the frozen dataclass
    prevents field reassignment after creation.
    """

    def test_keeps_method_metadata(self) -> None:
        method_information = MethodInformation(name="build_value", group="public", original_index=4)
        self.assertEqual("build_value", method_information.name, msg="Expected keeps method metadata; assertEqual failed.")
        self.assertEqual("public", method_information.group, msg="Expected keeps method metadata; assertEqual failed.")
        self.assertEqual(4, method_information.original_index, msg="Expected keeps method metadata; assertEqual failed.")

    def test_is_immutable(self) -> None:
        method_information = MethodInformation(name="build_value", group="public", original_index=4)
        with self.assertRaises(Exception, msg="Expected immutable method information to reject attribute mutation."):
            method_information.name = "other"  # type: ignore[misc]
