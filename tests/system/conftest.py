from pathlib import Path
import os
import shutil
import subprocess
import sys
from tempfile import mkdtemp
from typing import Iterator

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig):
    return [
        str(pytestconfig.rootdir.join('docker-compose.yml')),
        str(Path(__file__).parent / 'docker-compose.override.yml'),
    ]


@pytest.fixture(scope='session')
def scanomatic(request):
    mode = _system_test_mode()
    if mode == 'docker':
        return request.getfixturevalue('scanomatic_docker')
    return request.getfixturevalue('scanomatic_local')


@pytest.fixture(scope='session')
def scanomatic_docker(docker_ip, docker_services):
    def is_responsive(url: str) -> bool:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException:
            return False
        else:
            return True

    url = 'http://{}:{}'.format(
        docker_ip,
        docker_services.port_for('scanomatic', 5000),
    )
    docker_services.wait_until_responsive(
        timeout=30, pause=0.1,
        check=lambda: (
            is_responsive(url + '/fixtures')
            and is_responsive(url + '/api/status/server')
        ),
    )
    return url


@pytest.fixture(scope='session')
def scanomatic_local() -> Iterator[str]:
    root = Path(__file__).resolve().parents[2]
    local_data_root = Path(mkdtemp(prefix='som-system-tests-'))
    scanomatic_data = local_data_root / '.scan-o-matic'
    _prepare_local_runtime_data(scanomatic_data)
    _prepare_local_projects_root()

    env = os.environ.copy()
    env['SCANOMATIC_DATA'] = str(scanomatic_data)
    pythonpath = env.get('PYTHONPATH', '').strip()
    env['PYTHONPATH'] = f"{root}:{pythonpath}" if pythonpath else str(root)

    server_cmd = [sys.executable, str(root / 'scripts' / 'scan-o-matic_server')]
    ui_cmd = [
        sys.executable,
        str(root / 'scripts' / 'scan-o-matic'),
        '--host',
        '127.0.0.1',
        '--port',
        '5000',
        '--no-browser',
    ]

    rpc_process = subprocess.Popen(server_cmd, cwd=root, env=env)
    ui_process = subprocess.Popen(ui_cmd, cwd=root, env=env)

    url = 'http://127.0.0.1:5000'
    _wait_until_responsive(url)

    try:
        yield url
    finally:
        _terminate_process(ui_process)
        _terminate_process(rpc_process)
        shutil.rmtree(local_data_root, ignore_errors=True)


def _system_test_mode() -> str:
    requested = os.environ.get('SOM_SYSTEM_TEST_MODE', 'auto').strip().lower()
    if requested in ('docker', 'local'):
        return requested
    return 'docker' if _docker_is_usable() else 'local'


def _docker_is_usable() -> bool:
    if shutil.which('docker') is None:
        return False
    try:
        result = subprocess.run(
            ['docker', 'info'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (subprocess.SubprocessError, OSError):
        return False
    return result.returncode == 0


def _prepare_local_runtime_data(scanomatic_data: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    config_src = root / 'data' / 'config'
    config_dst = scanomatic_data / 'config'
    shutil.copytree(config_src, config_dst, dirs_exist_ok=True)

    ccc_src = root / 'tests' / 'system' / 'data' / 'TESTUMz.ccc'
    ccc_dst = config_dst / 'ccc' / 'TESTUMz.ccc'
    ccc_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ccc_src, ccc_dst)


def _prepare_local_projects_root() -> None:
    root = Path(__file__).resolve().parents[2]
    projects_root = Path('/somprojects')
    test_project_dir = projects_root / 'testproject'
    upload_dir = projects_root / 'my' / 'project'
    shutil.rmtree(test_project_dir, ignore_errors=True)
    shutil.rmtree(upload_dir, ignore_errors=True)
    test_project_dir.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(
        root / 'tests' / 'system' / 'data' / 'testproject.project.compilation',
        test_project_dir / 'testproject.project.compilation',
    )
    shutil.copyfile(
        (
            root / 'tests' / 'system' / 'data' /
            'testproject.project.compilation.instructions'
        ),
        test_project_dir / 'testproject.project.compilation.instructions',
    )


def _wait_until_responsive(url: str, timeout: int = 30) -> None:
    import time

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if (
                requests.get(url + '/fixtures').ok
                and requests.get(url + '/api/status/server').ok
            ):
                return
        except requests.RequestException:
            pass
        time.sleep(0.2)
    raise RuntimeError(f'Scan-o-Matic did not become responsive at {url}')


def _terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


@pytest.fixture(
    scope='function',
    ids=['chrome', 'firefox'],
    params=['chrome', 'firefox'],
)
def browser(request):
    driver: WebDriver
    if request.param == 'chrome':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
    else:
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('-headless')
        firefox_esr = shutil.which('firefox-esr')
        if firefox_esr:
            firefox_options.binary_location = firefox_esr
        driver = webdriver.Firefox(options=firefox_options)

    yield driver
    driver.quit()
