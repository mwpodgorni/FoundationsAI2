from typing import Any
from sklearn import preprocessing
import pandas as pd
import numpy as np

import copy
from math import log2


# We create a data structure for a Decision Node.
# Each node  will contain the information of each
# splitting decision made by the ID2 algorithm.
class DecisionNode(object):
    def __init__(self):
        # Holds information of either the attribute used for the split,
        # or the final value that the splits lead to.
        self.testValue = None
        # Stores the children nodes.
        self.daughterNodes = {}
        # Same as daughterNodes, but will be used for visualizing the tree.
        self.daughterNodesVisual = {}
        # Possible values that the attribute can take.
        self.possibleValues = []

    # Used for visualizing the tree at the end.
    def updateVisual(self):
        self.daughterNodesVisual = copy.copy(self.daughterNodes)
        for key in self.daughterNodesVisual.keys():
            subNode = self.daughterNodesVisual[key]
            value = subNode.testValue
            self.daughterNodesVisual[key] = value

    # Executes the ID3 algorithm on the root node.
    def execVisualization(self, level):
        if self.daughterNodes:
            print("________")
            print("***** LEVEL ", level, " *****")
            print("NODE:   ", self.testValue)
            print(self.possibleValues)
            self.updateVisual()
            print(self.daughterNodesVisual)
            childrenValues = self.daughterNodes.values()
            for node in childrenValues:
                node.execVisualization(level + 1)


# Function for computing the entropy using a set of examples.
def computeEntropy(examples):
    # Get number of examples
    # exampleCount = examples.length()
    print(examples)
    rows, _ = examples.shape
    exampleCount = rows
    # Check if we only have one --> if so, entropy is 0
    if exampleCount == 0:
        return 0
    # Else, we need to keep a tally of how many of
    # each different kind of action we have
    unique, counts = np.unique(examples[:, -1], return_counts=True)
    actionTallies = dict(zip(unique, counts))
    actionTallies = list(actionTallies.values())
    actionCount = len(actionTallies)
    actionTallies = np.array(actionTallies)
    # If we have only one action, then entropy is 0
    if actionCount == 0:
        return 0
    # Otherwise, start with 0 entropy...
    entropy = 0
    # ... and add the contribution of each action to entropy
    for actionTally in actionTallies:
        proportion = actionTally / exampleCount
        entropy -= proportion * log2(proportion)
    # Finally, return the total entropy
    return entropy


# Function for splitting a set of examples into sub-sets
# using a given attribute as the division criterion.
def splitByAttribute(examples, attribute):
    # Save the ID of the given attribute from the myAttributes list.
    attribute_id = myAttributes.index(attribute)
    # We create a set of lists as a dictionary with the form:
    # keys:     -> attribute's values
    # values:   -> list of the various examples with that value
    # This way, we can access each list by attribute value.
    sets: dict[Any, np.ndarray] = {}

    # Loop through each example...
    for example in examples:
        # ... and assign it to the right sub-set
        x = int(example[attribute_id])
        # If the value is already present as a key,
        # append the new example in that list.
        if x in sets:
            sets[example[attribute_id]] += example
        # Otherwise, create a new list.
        else:
            sets[example[attribute_id]] = example[np.newaxis]

    # Return the sets.
    return np.array(list(sets.values()))


# Function for computing the entropy of a given set of sets.
def entropyOfSets(sets, exampleCount):
    # Start with zero entropy
    entropy = 0
    # Get the entropy contribution of each set
    for set in sets:
        # Calculate the proportion of the whole in this set
        proportion = len(set) / exampleCount
        # Calculate entropy contribution
        entropy -= proportion * computeEntropy(set)
    # Return the total entropy
    return entropy


# Main function for actually building the tree.
def makeTree(examples, attributes, decisionNode):
    # Calculate our initial entropy
    initialEntropy = computeEntropy(examples)

    # If we have no entropy, we can't divide further
    if initialEntropy <= 0:
        t = examples[0][-1]
        decisionNode.testValue = encoder.inverse_transform([t])
        return
    exampleCount, _ = examples.shape

    # Hold the best found split so far
    bestInformationGain = 0
    bestSplitAttribute = None
    bestSets = None

    # Go through each attribute
    for attribute in attributes:
        # Perform the split
        sets = splitByAttribute(examples, attribute)

        # Find overall entropy and information gain
        overallEntropy = entropyOfSets(sets, exampleCount)
        informationGain = initialEntropy - overallEntropy

        # Check if we got the best so far
        if informationGain > bestInformationGain:
            bestInformationGain = informationGain
            bestSplitAttribute = attribute
            bestSets = sets

    # Set the decision node's test
    decisionNode.testValue = bestSplitAttribute
    # And the various branches of the best attribute
    bestSplitAttribute_id = myAttributes.index(bestSplitAttribute)
    unique, counts = np.unique(examples[:, bestSplitAttribute_id], return_counts=True)
    results = dict(zip(unique, counts))
    possibleValues = list(results.keys())
    decisionNode.possibleValues = possibleValues

    # The list of attributes to pass on down the tree
    # should have the one we're using removed
    newAttributes = copy.copy(attributes)
    newAttributes.remove(bestSplitAttribute)

    # Fill the daughter nodes

    for set in bestSets:
        # Find the value of the attribute in this set
        attributeValue = set[0][bestSplitAttribute_id]
        # Create a daughter node for the tree
        daughter = DecisionNode()
        # Add to the tree
        decisionNode.daughterNodes[attributeValue] = daughter
        # Recurse
        makeTree(set, newAttributes, daughter)


# Store the attribute we are trying to predict.
# In the book's terminology, the actions are the
# "end goal" we are trying to predict.
myActions = ["God", "S", "A", "B", "C", "D", "E"]

# League of Legends Champion Stats 12.4
# Some data manipulation to extract the data and re-shape it
# into usable format for our algorithm. The end result will be
# a 2D table with a champion's stats on each row, and the
# various attributes in each column.
dataset = pd.read_csv("smaller_dataset.csv", sep=";")
dataset["Win %"] = dataset["Win %"].str.replace("%", "").astype(float)
dataset["Role %"] = dataset["Role %"].str.replace("%", "").astype(float)
dataset["Pick %"] = dataset["Pick %"].str.replace("%", "").astype(float)
dataset["Ban %"] = dataset["Ban %"].str.replace("%", "").astype(float)

# The input data for our training.
input = dataset[
    ["Score", "Trend", "Win %", "Role %", "Pick %", "Ban %", "KDA"]
].to_numpy()
# The output i.e. the column of what we are trying to predict.
output = dataset["Tier"].to_numpy()

# We need to encode the "GOD", "A", ... ranks into labels that can be read
# and used by the algorithm i.e. 0, 1, 2, ....
# Initialize scikit-learn's LabelEncoder object.
encoder = preprocessing.LabelEncoder()
# Fit it to our possible outcomes i.e. the various ranks of champions.
encoder.fit(myActions)
tierCopy = dataset[["Tier"]]
# Compute the encoded version.
encodedTier = encoder.transform(np.array(tierCopy).flatten().transpose()).astype(float)

# Convert all the values inside our dataset to INTs.
myExamples = np.c_[input, encodedTier].astype(int)
# Store the attributes into a separate column.
myAttributes = list(dataset.columns)[4:]


# Initialise the root decision node.
myNode = DecisionNode()

# Execute the function for generating the ID3 tree.
makeTree(myExamples, myAttributes, myNode)
# print(myNode.daughterNodes)

# Execute the visualization function.
myNode.execVisualization(0)
