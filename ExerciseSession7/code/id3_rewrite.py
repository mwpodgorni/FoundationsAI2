from math import log2
from typing import Any, Self


class DecisionNode:
    def __init__(self) -> None:
        self.daughterNodes: dict[str, Self] = {}
        self.testValue: str | None = None
        self.possibleValues = []

    def print(self, level: int = 0):
        space = "  "
        print(space * level, "Level :", level)
        if self.testValue:
            print(space * level, "Test Value :", self.testValue)
        print("Possible Values :", self.possibleValues)
        for attribute in self.daughterNodes:
            node = self.daughterNodes[attribute]
            print(space * level, "Attribute : ", attribute)
            node.print(level + 1)


class Example:
    def __init__(self, action: str, values: list[Any]):
        self.action = action
        self.values = values

    def getValue(self, attribute_id: int) -> Any:
        return self.values[attribute_id]


def makeTree(examples: list[Example], attributes: list[str | None], decisionNode):
    # Calculate our initial entropy.
    initialEntropy = calculateEntropy(examples)

    # If we have no entropy, we can’t divide further.
    if initialEntropy <= 0:
        return

    # Find the number of examples.
    exampleCount = len(examples)

    if len(attributes) == 0:
        return
    # Find the number of examples.
    bestInformationGain = 0.0
    bestSplitAttribute = attributes[0]
    attributeIndex = 0
    bestSets = splitByAttribute(examples, attributeIndex)

    # Go through each attribute.
    for attribute in attributes:
        # Perform the split.
        if attribute is None:
            continue
        attributeIndex = attributes.index(attribute)
        sets = splitByAttribute(examples, attributeIndex)

        # Find overall entropy and information gain
        overallEntropy = entropyOfSets(sets, exampleCount)
        informationGain = initialEntropy - overallEntropy

        # Check if we’ve got the best so far.
        if informationGain > bestInformationGain:
            bestInformationGain = informationGain
            bestSplitAttribute = attribute
            bestSets = sets

    # Set the decision node’s test.
    decisionNode.testValue = bestSplitAttribute
    bestAttributeIndex = attributes.index(bestSplitAttribute)

    decisionNode.possibleValues = []
    for example in examples:
        value = example.getValue(bestAttributeIndex)
        if value not in decisionNode.possibleValues:
            decisionNode.possibleValues.append(value)

    # The list of attributes to pass on down the tree should
    # have the one we’re using removed.
    newAttributes = attributes.copy()
    newAttributes[bestAttributeIndex] = None

    attributeValue = None
    # Fill the daughter nodes.
    for set in bestSets.values():
        # Find the value for the attribute in this set.
        attributeValue = set[0].getValue(bestAttributeIndex)

        # Create a daughter node for the tree.
        daughter = DecisionNode()

        # Add it to the tree.
        decisionNode.daughterNodes[attributeValue] = daughter

        makeTree(set, newAttributes, daughter)


def splitByAttribute(examples: list[Example], attribute: int):
    sets: dict[Any, list[Example]] = {}

    for example in examples:
        value = example.getValue(attribute)

        if value in sets:
            sets[value].append(example)
        else:
            sets[value] = [example]

    return sets


def calculateEntropy(examples: list[Example]):
    exampleCount = len(examples)
    if exampleCount == 0:
        return 0.0

    actionTallies: dict[str, int] = {}

    for example in examples:
        if example.action in actionTallies:
            actionTallies[example.action] += 1
        else:
            actionTallies[example.action] = 1

    if len(actionTallies) == 0:
        return 0.0

    entropy = 0.0

    for actionTally in actionTallies.values():
        proportion = actionTally / exampleCount
        entropy -= proportion * log2(proportion)

    return entropy


def entropyOfSets(sets: dict[float, list[Example]], exampleCount: int):
    # Start with zero entropy.
    entropy = 0.0

    # Get the entropy contribution of each set.
    for set in sets.values():
        # Calculate the proportion of the whole in this set.
        proportion = len(set) / exampleCount

        # Calculate the entropy contribution.
        entropy -= proportion * calculateEntropy(set)

    # Return the total entropy.
    return entropy


allAttributes = [
    "Name",
    "Class",
    "Role",
    "Score",
    "Trend",
    "Win %",
    "Role %",
    "Pick %",
    "Ban %",
    "KDA",
]
# fmt: off
allExamples =  [
Example("God",["Aatrox","Fighter","TOP",78.04,18.05,50.05,93.07,7.05,3.39,1.91]),
Example("God",["Aatrox","Fighter","TOP",78.04,18.05,50.05,93.07,7.05,3.39,1.91]),
Example("God",["Ahri","Mage","MID",95.45,0.23,52.32,94.53,14.40,13.64,2.57]),
Example("S",["Akali","Assassin","MID",69.59,4.82,49.62,66.35,8.45,18.34,2.31]),
Example("A",["Akali","Assassin","TOP",56.22,-18.57,48.17,33.04,3.93,18.34,2.04]),
Example("A",["Akshan","Marksman","MID",52.94,-1.48,50.23,58.16,3.94,16.16,2.19]),
Example("A",["Akshan","Marksman","TOP",49.75,9.18,51.97,34.63,2.28,16.16,1.9]),
Example("B",["Alistar","Tank","SUPPORT",43.9,0.9,49.17,96.48,2.94,0.64,2.46]),
Example("B",["Amumu","Tank","JUNGLE",44.24,-0.71,50.15,80.89,2.82,1.34,2.48]),
Example("C",["Amumu","Tank","SUPPORT",37.03,7.73,48.59,17.51,0.32,1.34,2.02]),
Example("A",["Anivia","Mage","MID",53.6,0.85,52.36,82.14,2.90,2.96,2.56]),
Example("D",["Anivia","Mage","SUPPORT",33.39,2.21,46.38,11.84,0.38,2.91,2.11]),
Example("A",["Annie","Mage","MID",49.02,1.63,52.41,86.20,1.86,0.75,2.31]),
Example("B",["Aphelios","Marksman","ADC",45.36,1.67,47.08,98.01,9.11,1.59,2.01]),
Example("B",["Ashe","Marksman","ADC",45.56,0.48,49.75,90.10,5.47,0.87,2.32])]

tree = DecisionNode()
makeTree(allExamples, allAttributes, tree)

tree.print()
