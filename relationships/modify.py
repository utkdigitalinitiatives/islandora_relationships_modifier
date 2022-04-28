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

    def get_parent_of_pid(self, pid):
        """ Gets the membership of a specific PID.
        Args:
            pid (str): The persistent identifier to the object where you want to add the relationship.
        Returns:
            str: The persistent identifier of the first object the specified pid belongs to.
        Examples:
            >>> FedoraObject().get_parent_of_pid('bookColl:296')
            "info:fedora/bookColl:295"
        """
        r = requests.get(
            f"{self.fedora_url}/fedora/objects/{pid}/relationships?subject=info:fedora/{quote(pid, safe='')}"
            f"&predicate={quote('info:fedora/fedora-system:def/relations-external#isMemberOf', safe='')}",
            auth=self.auth,
        )
        if r.status_code == 200:
            response = r.content.decode("utf-8", "strict")
            parent = response.split(
                '<isMemberOf xmlns="info:fedora/fedora-system:def/relations-external#" rdf:resource="'
            )[1].split('"/>')[0]
            return parent
        else:
            raise Exception(
                f"Unable to find relationships to {pid}. Returned {r.status_code}."
            )

    def get_sequence_number(self, pid):
        """Find sequence number of pid if it exists.
        Args:
            pid (str): The persistent identifier to the object where you want to add the relationship.
        Returns:
            str: The sequence number of the requested PID to its parent.
        Examples:
            >>> FedoraObject().get_sequence_number('bookColl:296')
            "63"
        """
        r = requests.get(
            f"{self.fedora_url}/fedora/objects/{pid}/relationships?subject=info:fedora/{quote(pid, safe='')}"
            f"&predicate={quote('http://islandora.ca/ontology/relsext#isSequenceNumber', safe='')}",
            auth=self.auth,
        )
        if r.status_code == 200:
            response = r.content.decode("utf-8", "strict")
            parent = response.split(
                '<isSequenceNumber xmlns="http://islandora.ca/ontology/relsext#">'
            )[1].split('</isSequenceNumber>')[0]
            return parent
        else:
            raise Exception(
                f"Unable to find relationships to {pid}. Returned {r.status_code}."
            )

    def convert_book_to_compound_object(self, pid):
        """Convert a book to a compound object.
        Args:
            pid (str): The persistent identifier to the object where you want to add the relationship.
        Returns:
            str: A message stating that the request was successful.
        Examples:
            >>> FedoraObject().purge_relationship(pid="test:6")
            'test:6 is now a compound object and no longer a book.'
        """
        subject = f'info:fedora/{pid}'
        predicate = 'info:fedora/fedora-system:def/model#hasModel'
        # Make the object a compound object
        self.add_relationship(pid, subject, predicate, 'info:fedora/islandora:compoundCModel', is_literal=False)
        # Remove the book type
        self.purge_relationship(pid, subject, predicate, 'info:fedora/islandora:bookCModel', is_literal=False)
        return f"{pid} is now a compound object and no longer a book."

    def convert_page_to_part_of_compound_object(self, pid):
        """Convert a page to a large image and part of a compound object.
        Args:
            pid (str): The persistent identifier of the part.
        Returns:
            dict: A dict with messaging for each part and whether the operation was successful.
        """
        pid_parent = self.get_parent_of_pid(pid)
        sequence_number = self.get_sequence_number(pid)
        message = {}
        # Add new relationships
        # 1. Make Pid Constituent Of Parent Pid
        message['added isConstituentOf'] = self.add_relationship(
            pid,
            subject=f'info:fedora/{pid}',
            predicate="info:fedora/fedora-system:def/relations-external#isConstituentOf",
            obj=pid_parent,
            is_literal=False
        )
        # 2. Make a Large Image
        message['converted to large image'] = self.add_relationship(
            pid, f'info:fedora/{pid}',
            'info:fedora/fedora-system:def/model#hasModel',
            'info:fedora/islandora:sp_large_image_cmodel',
            is_literal=False
        )
        # 3. Add compound sequence relationship
        message['added sequence of escaped pid'] = self.add_relationship(
            pid,
            subject=f'info:fedora/{pid}',
            predicate=f'http://islandora.ca/ontology/relsext#isSequenceNumberOf{pid_parent.rstrip().replace("info:fedora/", "").replace(":","_")}',
            obj=sequence_number.rstrip(),
            is_literal=True
        )
        # Wipe out old relationships
        # 1. Remove Page Content Model
        message['removed page content model'] = self.purge_relationship(
            pid,
            subject=f'info:fedora/{pid}',
            predicate='info:fedora/fedora-system:def/model#hasModel',
            obj='info:fedora/islandora:pageCModel',
            is_literal=False
        )
        # 2. Remove is Page Of
        message['removed isPageOf'] = self.purge_relationship(
            pid,
            subject=f'info:fedora/{pid}',
            predicate='http://islandora.ca/ontology/relsext#isPageOf',
            obj=pid_parent.rstrip(),
            is_literal=False
        )
        # 3. Remove is Sequence Number Of
        message['removed isSequenceNumberOf'] = self.purge_relationship(
            pid,
            subject=f'info:fedora/{pid}',
            predicate='http://islandora.ca/ontology/relsext#isSequenceNumber',
            obj=sequence_number.rstrip(),
            is_literal=True
        )
        # 4. Remove is Section Of
        message['removed isSection'] = self.purge_relationship(
            pid,
            subject=f'info:fedora/{pid}',
            predicate='http://islandora.ca/ontology/relsext#isSection',
            obj="1",
            is_literal=True
        )
        return message
        # 5. Remove is Page Number
        message['removed isPageNumber'] = self.purge_relationship(
            pid,
            subject=f'info:fedora/{pid}',
            predicate='http://islandora.ca/ontology/relsext#isPageNumber',
            obj=sequence_number.rstrip(),
            is_literal=True
        )


if __name__ == "__main__":
    FedoraObject().get_parent_of_pid('bookColl:296')
