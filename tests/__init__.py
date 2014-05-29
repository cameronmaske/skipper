from skipper.project import Project

import pytest
import mock


@pytest.fixture(scope="module")
def project():
    host = mock.MagicMock()
    project = Project(name="test", host=host)
    return project
