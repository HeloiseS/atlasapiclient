# Write tests for the exceptions in atlasapiclient.exceptions

import pytest
from atlasapiclient.exceptions import ATLASAPIClientError

class TestATLASAPIClientError():
    def test_ATLASAPIClientError(self):
        with pytest.raises(ATLASAPIClientError):
            raise ATLASAPIClientError