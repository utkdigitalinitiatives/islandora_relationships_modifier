import requests
from urllib.parse import quote


class FedoraObject:
    def __init__(
            self,
            fedora_url="http://localhost:8080",
            auth=("fedoraAdmin", "fedoraAdmin")
    ):
        self.fedora_url = fedora_url
        self.auth = auth

    def add_relationship(self, pid, subject, predicate, obj, is_literal="true"):
        """Add a relationship to a digital object or datastream.
        Args:
            pid (str): The persistent identifier to the object where you want to add the relationship.
            subject (str): The subject of the relationship.  This should refer to the pid (for external relationships)
            or the dsid (for internal relationships). For
            predicate (str): The predicate of the new relationship.
            obj (str): The object of the new relationship.  Can refer to a graph or a literal.
            is_literal (str): This defaults to "true" but can also be "false." It specifies whether the object is a graph or a literal.
        Returns:
            int: The status code of the post request.
        Examples:
            >>> FedoraObject().add_relationship(pid="test:6", subject="info:fedora/test:6",
            ... predicate="info:fedora/fedora-system:def/relations-external#isMemberOfCollection",
            ... obj="info:fedora/islandora:test", is_literal="false",)
            200
        """
        r = requests.post(
            f"{self.fedora_url}/fedora/objects/{pid}/relationships/new?subject={quote(subject, safe='')}"
            f"&predicate={quote(predicate, safe='')}&object={quote(obj, safe='')}&isLiteral={is_literal}",
            auth=self.auth,
        )
        if r.status_code == 200:
            return r.status_code
        else:
            raise Exception(
                f"Unable to add relationship on {pid} with subject={subject}, predicate={predicate}, and object={obj}, "
                f"and isLiteral as {is_literal}.  Returned {r.status_code}."
            )

    def purge_relationship(self, pid, subject, predicate, obj, is_literal="true"):
        """Purge a relationship to a digital object or datastream.
                Args:
                    pid (str): The persistent identifier to the object where you want to add the relationship.
                    subject (str): The subject of the relationship.  This should refer to the pid (for external relationships)
                    or the dsid (for internal relationships). For
                    predicate (str): The predicate of the new relationship.
                    obj (str): The object of the new relationship.  Can refer to a graph or a literal.
                    is_literal (str): This defaults to "true" but can also be "false." It specifies whether the object is a graph or a literal.
                Returns:
                    int: The status code of the post request.
                Examples:
                    >>> FedoraObject().purge_relationship(pid="test:6", subject="info:fedora/test:6",
                    ... predicate="info:fedora/fedora-system:def/relations-external#isMemberOfCollection",
                    ... obj="info:fedora/islandora:test", is_literal="false",)
                    200
                """
        r = requests.delete(
            f"{self.fedora_url}/fedora/objects/{pid}/relationships?subject={quote(subject, safe='')}"
            f"&predicate={quote(predicate, safe='')}&object={quote(obj, safe='')}&isLiteral={is_literal}",
            auth=self.auth,
        )
        if r.status_code == 200:
            return r.status_code
        else:
            raise Exception(
                f"Unable to purge relationship on {pid} with subject={subject}, predicate={predicate}, and object={obj}, "
                f"and isLiteral as {is_literal}.  Returned {r.status_code}."
            )

    def convert_book_to_compound_object(self, pid):
        """Convert a book to a compound object.
                Args:
                    pid (str): The persistent identifier to the object where you want to add the relationship.
                Returns:
                    int: The status code of the post request.
                Examples:
                    >>> FedoraObject().purge_relationship(pid="test:6")
                        200
        """
        subject = f'info:fedora/{pid}'
        predicate = 'info:fedora/fedora-system:def/model#hasModel'
        # Make the object a compound object
        self.add_relationship(pid, subject, predicate, 'info:fedora/islandora:compoundCModel', is_literal=False)
        # Remove the book type
        self.purge_relationship(pid, subject, predicate, 'info:fedora/islandora:bookCModel', is_literal=False)
        return f"{pid} is now a compound object and no longer a book."


if __name__ == "__main__":
    FedoraObject().get_relationships_with_pid('bookColl:295')
