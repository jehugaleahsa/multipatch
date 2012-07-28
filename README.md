multipatch
==========

An extension for composing Mock's patch context manager.

It is not uncommon for multiple unit tests to require much of the same fixture setup. Many times, this just means the same types are mocked out for the scope of a unit test. Mock's context managers do not compose well, meaning you can't easily build up a list of patches. The purpose of multipatch is to allow you to easily build a context manager for composing patches and control their lifetimes.

Here is an example using multipatch:

    from mock import patch
    from multpatch import multipatch
    from unittest import TestCase


    class Dependency1(object):
      def getNumber(self): 
        return 1
    
    
    class Dependency2(object):
      def getNumber(self):
        return 2


    class SUT(object):
      def foo(self):
        dep1 = Dependency1()
        dep2 = Dependency2()
        return dep1.getNumber() + dep2.getNumber()
    
    class SUTTestCase(TestCase):
      def testFoo_mockDepsOnlyInCntx(self):
        sut = SUT()
    
        with multipatch(
          dep1=mock.patch('__main__.Dependency1'),
          dep2=mock.patch('__main__.Dependency2')
        ) as patcher:
          # reference dependencies by name
          patcher.dep1.getNumber.return_value = 3
          patcher.dep2.getNumber.return_value = 4
      
          result = sut.foo() # adds mocked return values
      
          self.assertEqual(7, result)
      
        result = sut.foo() # adds the original return values
        self.assertEqual(2, result)
        
The patch collection returned from multipatch can be returned from a function. New multipatches can be created by passing other multipatches to the `multipatch` function. This means you can easily compose patches together. Instead of dealing with the tuples that `nest` provides or with the one-and-done nature of `patch.multiple`. You can access your mock objects by name and reuse patches via composition.

Multipatches can also be used anywhere a `patch` can be used, except as a decorator. This means if you want to merge two multipatches with conflicting mock names, you can just make one of the multipatches a patch by giving it a name:

    def getPatches():
        nested = multipatch(class1=patch('package.module.ClassName1'))
        patch = multipatch(nested=nested, class1=patch('package.module.ClassName2'))
        # patch.nested.class1
