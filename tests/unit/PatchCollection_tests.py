import unittest


class PatchCollectionTester(unittest.TestCase):

    def testpatch_noModuleName_createsEmptyPatchCollection(self):
        """
        If we call `patch` without any arguments, it will create
        an empty PatchCollection.
        """
        pass
