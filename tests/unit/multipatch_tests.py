import mock
import unittest

from multipatch import multipatch


class MultipatchTester(unittest.TestCase):
    """Tests the multipatch function."""

    def testMultipatch_patchTwoTypes_bothPatched(self):
        """If we combine two patches, they should be patched together."""
        # record the old class types
        Class1Original = Class1
        Class2Original = Class2

        with multipatch(
            class1=mock.patch('multipatch_tests.Class1'),
            class2=mock.patch('multipatch_tests.Class2'),
        ) as patcher:
            self.assertIsInstance(Class1(), mock.Mock,
                "The first class was not patched.")
            self.assertIsInstance(Class2(), mock.Mock,
                "The second class was not patched.")

        self.assertIsInstance(Class1(), Class1Original,
            "The first class was not reverted.")
        self.assertIsInstance(Class2(), Class2Original,
            "The second class was not reverted.")

    def testMultipatch_patchOneType_patched(self):
        """We can wrap a single patch."""
        Class1Original = Class1

        with multipatch(
            class1=mock.patch('multipatch_tests.Class1')
        ) as patcher:
            self.assertIsInstance(Class1(), mock.Mock,
                "The class was not patched.")

        self.assertIsInstance(Class1(), Class1Original,
            "The class was not reverted.")

    def testMultipatch_patchType_started_mocksAvailable(self):
        """Patching a type adds it as an attribute."""
        patch1 = mock.patch('multipatch_tests.Class1')
        patcher = multipatch(class1=patch1)

        try:
            patcher.start()
            self.assertTrue(hasattr(patcher, 'class1'),
                "The patch was not added as an attribute.")
    
            self.assertIsInstance(patcher.class1, mock.Mock,
                "The patch attribute is not a mock.")
    
            self.assertIs(patcher.class1, patcher.class1,
                "The same mock was not returned for the attribute.")
        finally:
            patcher.stop()

        self.assertFalse(hasattr(patcher, 'class1'),
            "The patch should not longer be an attribute.")

    def testMultipatch_patchType_notStarted_mocksHidden(self):
        """We can only see mocks once the context is started."""
        patch1 = mock.patch('multipatch_tests.Class1')
        patcher = multipatch(class1=patch1)

        self.assertFalse(hasattr(patcher, 'class1'),
            "The patcher should not expose the mock until started.")

    def testMultipatch_requestSameAttribute_recieveSameMock(self):
        """The same mock should be returned for a patch."""
        with multipatch(
            class1=mock.patch('multipatch_tests.Class1')
        ) as patcher:
            self.assertTrue(hasattr(patcher, 'class1'),
                "An attribute for the patch was not added.")
            mock1 = patcher.class1
            mock2 = patcher.class1
            self.assertIs(mock1, mock2, 'The same mock was not returned.')

    def testMultipatch_otherMulti_collapses(self):
        """Support composing by stealing other patches."""
        patch1 = multipatch(class1=mock.patch('multipatch_tests.Class1'))
        patch2 = multipatch(class2=mock.patch('multipatch_tests.Class2'))
        patch = multipatch(patch1, patch2)
        with patch as patcher:
            self.assertTrue(hasattr(patcher, 'class1'), 
                'The first patch was not copied.')
            self.assertTrue(hasattr(patcher, 'class2'), 
                'The second patch was not copied.')

    def testMultipatch_duplicatePatch_pm_raisesValueError(self):
        """Can't share patch names between patch and multipatch."""
        patch1 = multipatch(class1=mock.patch('multipatch_tests.Class1'))
        self.assertRaises(
            ValueError,
            multipatch,
            patch1, # has class1
            class1=mock.patch('multipatch_tests.Class2')
        )

    def testMultipatch_duplicatePatch_mm_raisesValueError(self):
        """Can't share patch named between two multipatches."""
        patch1 = multipatch(class1=mock.patch('multipatch_tests.Class1'))
        patch2 = multipatch(class1=mock.patch('multipatch_tests.Class1'))
        self.assertRaises(ValueError, multipatch, patch1, patch2)

    def testMultipatch_treatMultiLikePatch_supportsInterface(self):
        """Multipatches can be treated like patches."""
        other = multipatch(class1=mock.patch('multipatch_tests.Class1'))
        patch = multipatch(other=other)
        with patch as patcher:
            self.assertTrue(hasattr(patcher, 'other'),
                'The multipatcher was not stored as an attribute.')
            self.assertTrue(hasattr(patcher.other, 'class1'),
                'The patcher was mocked by accident.')
            self.assertIsInstance(patcher.other.class1, mock.Mock,
                'The multipatcher stopped creating mocks.')


class Class1(object):
    pass


class Class2(object):
    pass
