##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test hookup
"""
import os
import unittest
import zope.event
import zope.interface
from zope.component import testing, provideAdapter
from zope.testing import doctest

from zope.wfmc import interfaces, process

def tearDown(test):
    testing.tearDown(test)
    zope.event.subscribers.pop()

def setUp(test):
    test.globs['this_directory'] = os.path.dirname(__file__)
    testing.setUp(test)
    provideAdapter(process.PythonExpressionEvaluator)

@zope.interface.implementer(
    interfaces.IAbortWorkItem, interfaces.IRevertableWorkItem)
class WorkItemStub(object):

    def __init__(self, participant, process, activity):
        self.participant = participant
        self.process = process
        self.activity = activity

    def start(self, *args):
        self.args = args
        print 'Workitem %i for activity %r started.' % (
            self.id, self.activity.definition.id)

    def abort(self):
        print 'Workitem %i for activity %r aborted.' % (
            self.id, self.activity.definition.id)

    def revert(self):
        print 'Workitem %i for activity %r reverted.' % (
            self.id, self.activity.definition.id)


def test_multiple_input_parameters():
    """
    We'll create a very simple process that inputs two variables and
    has a single activity that just outputs them.

    >>> from zope.wfmc import process
    >>> pd = process.ProcessDefinition('sample')
    >>> from zope import component, interface
    >>> component.provideUtility(pd, name=pd.id)

    >>> pd.defineParameters(
    ...     process.InputParameter('x'),
    ...     process.InputParameter('y'),
    ...     )

    >>> pd.defineActivities(
    ...    eek = process.ActivityDefinition(),
    ...    ook = process.ActivityDefinition(),
    ...    )

    >>> pd.defineTransitions(process.TransitionDefinition('eek', 'ook'))

    >>> pd.defineApplications(
    ...     eek = process.Application(
    ...         process.InputParameter('x'),
    ...         process.InputParameter('y'),
    ...         )
    ...     )

    >>> pd.activities['eek'].addApplication('eek', ['x', 'y'])

    >>> from zope.wfmc import interfaces

    >>> class Participant(object):
    ...     zope.component.adapts(interfaces.IActivity)
    ...     zope.interface.implements(interfaces.IParticipant)
    ...
    ...     def __init__(self, activity, process):
    ...         self.activity = activity

    >>> from zope.wfmc.attributeintegration import AttributeIntegration
    >>> integration = AttributeIntegration()
    >>> pd.integration = integration

    >>> integration.Participant = Participant


    >>> class Eek:
    ...     component.adapts(interfaces.IParticipant)
    ...     interface.implements(interfaces.IWorkItem)
    ...
    ...     def __init__(self, participant, process, activity):
    ...         self.participant = participant
    ...
    ...     def start(self, x, y):
    ...         print x, y


    >>> integration.eekWorkItem = Eek

    >>> proc = pd()
    >>> proc.start(99, 42)
    99 42
    """

def test_pickling():
    """
    >>> from zope.wfmc import process
    >>> pd = process.ProcessDefinition('sample')
    >>> from zope import component, interface
    >>> component.provideUtility(pd, name=pd.id)

    >>> pd.defineActivities(
    ...    eek = process.ActivityDefinition(),
    ...    ook = process.ActivityDefinition(),
    ...    )

    >>> pd.defineTransitions(process.TransitionDefinition('eek', 'ook'))

    >>> pd.defineApplications(
    ...     eek = process.Application(
    ...         process.InputParameter('x'),
    ...         process.InputParameter('y'),
    ...         )
    ...     )

    >>> pd.activities['eek'].addApplication('eek', ['x', 'y'])


    >>> proc = pd()

    >>> import pickle
    >>> s = pickle.dumps(proc)
    """

def test_inputoutput():
    """

    >>> from zope.wfmc import process
    >>> pd = process.ProcessDefinition('sample')
    >>> from zope import component, interface
    >>> component.provideUtility(pd, name=pd.id)

    >>> pd.defineParameters(
    ...     process.InputParameter('x'),
    ...     )

    >>> pd.defineActivities(
    ...    eek = process.ActivityDefinition(),
    ...    ook = process.ActivityDefinition(),
    ...    )

    >>> pd.defineTransitions(process.TransitionDefinition('eek', 'ook'))

    >>> pd.defineApplications(
    ...     eek = process.Application(
    ...         process.InputOutputParameter('x'),
    ...         )
    ...     )

    >>> pd.activities['eek'].addApplication('eek', ['x'])

    >>> class Participant(object):
    ...     def __init__(self, activity, process):
    ...         self.activity = activity

    >>> from zope.wfmc.attributeintegration import AttributeIntegration
    >>> integration = AttributeIntegration()
    >>> pd.integration = integration

    >>> integration.Participant = Participant

    >>> class Eek:
    ...     def __init__(self, participant, process, activity):
    ...         self.participant = participant
    ...
    ...     def start(self, x):
    ...         self.participant.activity.workItemFinished(self, x+1)


    >>> integration.eekWorkItem = Eek

    >>> proc = pd()
    >>> proc.start(1)
    >>> proc.workflowRelevantData.x
    2
    """

def test_wrong_number_process_args_error_message():
    """

    >>> from zope.wfmc import process
    >>> pd = process.ProcessDefinition('sample')
    >>> from zope import component, interface
    >>> component.provideUtility(pd, name=pd.id)
    >>> pd.defineActivities(
    ...    eek = process.ActivityDefinition(),
    ...    ook = process.ActivityDefinition(),
    ...    )
    >>> pd.defineTransitions(process.TransitionDefinition('eek', 'ook'))

    >>> proc = pd()
    >>> proc.start(1)
    Traceback (most recent call last):
    ...
    TypeError: Too many arguments. Expected 0. got 1
    """

def test_process_abort():
    """
    >>> from zope.wfmc import process
    >>> pd = process.ProcessDefinition('sample')
    >>> from zope import component, interface
    >>> component.provideUtility(pd, name=pd.id)

    >>> pd.defineActivities(
    ...    eek = process.ActivityDefinition(),
    ...    ook = process.ActivityDefinition(),
    ...    )

    >>> pd.defineTransitions(process.TransitionDefinition('eek', 'ook'))

    >>> pd.defineApplications(
    ...     eek = process.Application(
    ...         process.InputParameter('x'),
    ...         process.InputParameter('y'),
    ...         ),
    ...     ook = process.Application()
    ...     )

    >>> pd.activities['eek'].addApplication('eek', ['x', 'y'])
    >>> pd.activities['ook'].addApplication('ook')

    >>> from zope.wfmc.attributeintegration import AttributeIntegration
    >>> integration = AttributeIntegration()
    >>> integration.eekWorkItem = WorkItemStub
    >>> integration.ookWorkItem = WorkItemStub
    >>> integration.Participant = process.Participant
    >>> pd.integration = integration

    >>> proc = pd()
    >>> proc.workflowRelevantData.x = 1
    >>> proc.workflowRelevantData.y = 2

    >>> proc.start()
    Workitem 1 for activity 'eek' started.

    >>> proc.activities[1].workItemFinished(proc.activities[1].workitems[1][0])
    Workitem 1 for activity 'ook' started.

    >>> proc.abort()
    Workitem 1 for activity 'ook' aborted.
    Workitem 1 for activity 'eek' reverted.
    """


def test_suite():
    suite = unittest.TestSuite()
    for doctestfile in ['README.txt', 'xpdl.txt',
                        'xpdl-2.1.txt']:
        suite.addTest(doctest.DocFileSuite(
            doctestfile,
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE))
    suite.addTest(doctest.DocTestSuite(
        setUp=setUp, tearDown=testing.tearDown))
    return suite
