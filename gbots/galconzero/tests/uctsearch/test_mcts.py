import numpy as np

from uctsearch.mcts import childQ, childU, selectBestChild, MIN_CHILD_U, UCTNode, Mcts


def test_childQ():
    child_total_values = np.array([-1.5, 2.1, 0, 4])
    child_num_visits = np.array([3, 21, 0, 4])
    defaultQ = 0.3

    expectedChildQs = np.array([-0.5, 0.1, defaultQ, 1])

    childQs = childQ(child_total_values, child_num_visits, defaultQ)

    np.testing.assert_equal(expectedChildQs, childQs)


def test_childU():
    child_num_visits = np.array([9, 3, 3, 1])
    child_priors = np.array([0.5, 0.3, 0.2, 0])
    parentVisits = 16

    expectedChildUs = np.array([0.2, 0.3, 0.2, MIN_CHILD_U])

    childUs = childU(child_num_visits, child_priors, parentVisits)

    np.testing.assert_equal(expectedChildUs, childUs)


def test_selectBestChild():
    child_priors = np.array([0.5, 0.3, 0.2, 0])
    child_total_values = np.array([-1.5, 2.1, 0, 0])
    child_num_visits = np.array([9, 3, 3, 0])
    child_vloss = np.array([0, 0, 0, 0])

    parentVisits = 16
    defaultQ = 0.3
    parent_vloss = 0

    #expectedChildQs = np.array([-0.16666, 0.7, 0, 0.3])
    #expectedChildUs = np.array([0.2, 0.3, 0.2, MIN_CHILD_U])

    selectedChild = selectBestChild(child_total_values, child_num_visits,
                                    child_vloss, child_priors, parentVisits, parent_vloss, defaultQ)
    np.testing.assert_equal(1, selectedChild)


def test_selectBestChild_withVLoss():
    child_priors = np.array([0.5, 0.3, 0.2, 0])
    child_total_values = np.array([-1.5, 2.1, 0, 0])
    child_num_visits = np.array([9, 3, 3, 0])
    child_vloss = np.array([1, 3, 0, 0])

    parentVisits = 16
    defaultQ = 0.3
    parent_vloss = 5

    #expectedChildQs = np.array([-0.25, -0.15, 0, 0.3])
    #expectedChildUs = np.array([0.2083, 0.1964, 0.2291, MIN_CHILD_U])

    selectedChild = selectBestChild(child_total_values, child_num_visits,
                                    child_vloss, child_priors, parentVisits, parent_vloss, defaultQ)
    np.testing.assert_equal(2, selectedChild)


def test_getPrincipalVariation():
    node = UCTNode(None, None)
    node.child_number_visits = np.arange(10)

    selected = Mcts(None).getPrincipalVariation(node, False)
    np.testing.assert_equal(9, selected)


def test_getPrincipalVariation_stochastic():
    node = UCTNode(None, None)
    node.child_number_visits = np.arange(10)

    counts = np.zeros(10)

    for _ in range(1000):
        selected = Mcts(None).getPrincipalVariation(node, True)
        counts[selected] += 1

    assert counts[0] == 0
    assert counts[1] > 0
    assert counts[9] > counts[1]
