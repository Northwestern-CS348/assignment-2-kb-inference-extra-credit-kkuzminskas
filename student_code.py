import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment

    def help_supported_by_loop(self, inst_supported_by, curr_indent):
        """Help explain all values in the supported_by loop

        Args:
            inst_supported_by [Fact, Rule] - instance of supported by

        Returns:
            String
        """

        ret = ""
        indent = "  "

        if isinstance(inst_supported_by[0], Fact):
            sup_f = inst_supported_by[0]
            sup_r = inst_supported_by[1]
        else:
            sup_f = inst_supported_by[1]
            sup_r = inst_supported_by[0]

        if sup_f.asserted:
            assert_str_f = " ASSERTED\n"
        else:
            assert_str_f = "\n"

        if sup_r.asserted:
            assert_str_r = " ASSERTED\n"
        else:
            assert_str_r = "\n"


        ret += curr_indent + indent + indent + "fact: " + str(sup_f.statement) + assert_str_f

        ret += self.help_kb_explain(sup_f, curr_indent + indent + indent)

        # rule
        ret += curr_indent + indent + indent + "rule: ("
        for stat in sup_r.lhs:
            ret += str(stat) + ", "

        ret = ret[:-2]

        ret += ") -> " + str(sup_r.rhs) + assert_str_r

        ret += self.help_kb_explain(sup_r, curr_indent + indent + indent)

        return ret


    def help_kb_explain(self, fact_or_rule, curr_indent):
        """Explain facts or rules that are supported by other rules

        Args:
            fact_or_rule (Fact|Rule) - Fact or Rule that is to be explained

        Returns:
            string
        """

        # Student code goes here
        ret = ""
        indent = "  "


        if isinstance(fact_or_rule, Fact):
            # check if it is in the KB
            if not fact_or_rule in self.facts:
                return ""

            for f in self.facts:
                if fact_or_rule == f:
                    fact = f


            if not fact.supported_by:
                return ""

            # new line
            ret += curr_indent + indent + "SUPPORTED BY \n"

            for sup in fact.supported_by:
                ret += self.help_supported_by_loop(sup, curr_indent)


        elif isinstance(fact_or_rule, Rule):
            if not fact_or_rule in self.rules:
                return ""


            for r in self.rules:
                if r == fact_or_rule:
                    rule = r

            if not rule.supported_by:
                return ""

            # new line
            ret += curr_indent + indent + "SUPPORTED BY \n"

            for sup in rule.supported_by:
                ret += self.help_supported_by_loop(sup, curr_indent)

        else:
            print("Error: Input was not a fact or rule")
            return False;


        return ret;

    def kb_explain(self, fact_or_rule):
        """
        Explain where the fact or rule comes from

        Args:
            fact_or_rule (Fact or Rule) - Fact or rule to be explained

        Returns:
            string explaining hierarchical support from other Facts and rules
        """
        ####################################################
        # Student code goes here
        ret = ""
        indent = "  "

        if isinstance(fact_or_rule, Fact):
            # check if it is in the KB
            if not fact_or_rule in self.facts:
                return "Fact is not in the KB"

            for f in self.facts:
                if fact_or_rule == f:
                    fact = f


            ret = "fact: " + str(fact.statement)


            if fact.asserted:
                ret += " ASSERTED\n"
            else:
                ret += "\n"


            for sup in fact.supported_by:
                # new line
                ret += indent + "SUPPORTED BY \n"

                ret += self.help_supported_by_loop(sup, "")


        elif isinstance(fact_or_rule, Rule):
            # check if it is in the KB
            if not fact_or_rule in self.rules:
                return "Rule is not in the KB"


            for r in self.rules:
                if r == fact_or_rule:
                    rule = r

            ret = "rule: ("
            for stat in rule.lhs:
                ret += str(stat) + ", "

            ret = ret[:-2]

            ret += ") -> " + str(rule.rhs)

            if rule.asserted:
                ret += " ASSERTED\n"
            else:
                ret += "\n"


            for sup in rule.supported_by:
                # new line
                ret += indent + "SUPPORTED BY \n"

                ret += self.help_supported_by_loop(sup, "")

        else:
            print("Error: Input was not a fact or rule")
            return False;

        print(ret)
        return ret;




class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment
