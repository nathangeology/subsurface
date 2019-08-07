import abc as a


class AbstractInput(a.ABC):
    """
    Abstract base class for input classes, provides a uniform interface
    for all types of input so that downstream customers can get data in
    a way that doesn't require knowledge of its data source type.
     """
    filter = None
    source_name = None

    @a.abstractmethod
    def return_dictionary(self)->dict:
        """Override this method in child classes to provide a uniform input interface"""
        pass
