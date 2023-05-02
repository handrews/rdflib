import warnings
from urllib.parse import urlparse

from rdflib import URIRef

INVALID_URI = "https://example.{}.com"
VALID_RELATIVE_PATH = "foo/bar"
VALID_HTTPS_URI = "https://example.com/foo?x=y#bar"
VALID_EXAMPLE_URN = "urn:example:foo-bar-baz-qux?+CCResolve:cc=uk"
VALID_UUID_URN = "urn:uuid:0e5f5ff6-6c80-4786-84b9-4c121bb3ae9f"

if __name__ == "__main__":
    # By default, a warning is logged if validation fails
    # during the constructor, and an error raised during serialization
    invalid = URIRef(INVALID_URI)
    print(f"Default strictness allows <{invalid}>")
    print()
    try:
        invalid.n3()
        assert False, "Should be unreachable!"
    except ValueError as e:
        print(f"Got expected validation error serializing <{invalid}>:")
        print(f"\t{e}")
        print()
    try:
        URIRef(INVALID_URI, strict=True)
        assert False, "Should be unreachable!"
    except ValueError as e:
        print(f"Got expected validation error constructing <{invalid}>:")
        print(f"\t{e}")
        print()

    # Validation can check that there's a scheme
    u = URIRef(
        VALID_HTTPS_URI,
        validator=lambda u: bool(urlparse(u).scheme),
        strict=True,
    )

    # Validation can be disabled entirely, which can be dangerous
    wrong = URIRef(INVALID_URI, validator=lambda u: True)
    assert wrong.n3() == f"<{INVALID_URI}>"

    # Complex application-specific validation can be added.
    # This should be done with strict=True to avoid running
    # the expensive validation again at serialization time.
    try:
        from urnparse import URN8141, InvalidURNFormatError

        class URNStrictUUID(URIRef):
            @staticmethod
            def _validate(urn_str):
                try:
                    urn = URN8141.from_string(urn_str)
                    return urn.namespace_id == "uuid"
                except InvalidURNFormatError:
                    return False

            def __new__(cls, value):
                super().__new__(
                    cls,
                    value,
                    strict=True,
                    validator=cls._validate,
                )

        uuid = URNStrictUUID(VALID_UUID_URN)
        print(f"<{VALID_UUID_URN}> correctly considered a valid UUID URN")
        print()
        try:
            URNStrictUUID(VALID_EXAMPLE_URN)
            assert False, "Statement after failed validation should be unreachable"

        except ValueError as e:
            print(
                "Got expected UUID-URN-specific validation error serializing "
                f"<{VALID_EXAMPLE_URN}>:"
            )
            print(f"\t{e}")
            print()
            # Our example URN is still a valid URIRef in general.
            uriref = URIRef(VALID_EXAMPLE_URN, strict=True)
            print(f"<{VALID_EXAMPLE_URN}> correctly considered a valid URN")
            print()

    except ImportError:
        warnings.warn("URN validation example requires urnparse module, skipping...")
