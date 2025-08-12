from dataclasses import asdict, dataclass

from fabric import Connection, task
from invoke.context import Context

_DOCKER_PULL = "docker pull --platform=linux/amd64"
_DOCKER_BUILD = "docker buildx build --platform=linux/amd64 --build-arg BUILD_DEV=rex"
_c = Context()


@task
def env_prd(c):
    ev.switch_to_prd()


def _say_it(message: str):
    print(message)
    _c.run(f"say {message}")


@task
def docker_pull_base_image(c):
    c.run(f"{_DOCKER_PULL} {ev.DOCKER_BASE_IMAGE_TAG}")
    print("pull docker base image finished.")


def docker_build(c):
    print("build docker image...")
    c.run(f"{_DOCKER_BUILD} -t {ev.DOCKER_IMAGE_FULL_NAME} .")
    c.run("docker image prune -f")

    _say_it("build finished")


@task
def docker_push_image(c):
    print("push docker image to register...")

    c.run(f"docker push {ev.DOCKER_IMAGE_FULL_NAME}")
    print("push finished.")


@task
def docker_pull_image(c):
    c.run(f"{_DOCKER_PULL} {ev.DOCKER_IMAGE_FULL_NAME}")
    print("pull image finished.")


@task
def docker_send_image(c):
    print("send docker image to deploy server...")
    c.run(
        f'docker save {ev.DOCKER_IMAGE_FULL_NAME} | gzip | ssh {ev.DEPLOY_SSH_USER}@{ev.DEPLOY_SSH_HOST} -p {ev.DEPLOY_SSH_PORT} "gunzip | docker load"'
    )
    _say_it("send image finished")


@task
def build(c):
    docker_pull_base_image(c)
    docker_build(c)


def run_restart_script(c):
    c.run(f"cd {ev.DEPLOY_WORK_PATH} && ./RestartContainer.sh")


@dataclass
class EnvValue:
    APP_NAME = "ddns-clienter"

    # 目标机器信息
    DEPLOY_STAGE = "prd"
    DEPLOY_SSH_HOST = "192.168.200.66"
    DEPLOY_SSH_PORT = 22
    DEPLOY_SSH_USER = "root"

    @property
    def DEPLOY_WORK_PATH(self) -> str:
        data = f"/mnt/main/docker/{self.APP_NAME}"
        if self.DEPLOY_STAGE != "prd":
            data += f"-{self.DEPLOY_STAGE}"

        return data

    # Container Register 信息
    CR_HOST_NAME = "cr.h.rexzhang.com"
    CR_NAME_SPACE = "rex"

    # Docker Image 信息
    DOCKER_BASE_IMAGE_TAG = "crp.rexzhang.com/library/python:3.13-alpine"

    @property
    def DOCKER_IMAGE_FULL_NAME(self) -> str:
        name = f"{self.CR_HOST_NAME}/{self.CR_NAME_SPACE}/{self.APP_NAME}"
        if self.DEPLOY_STAGE != "prd":
            name += f"-{self.DEPLOY_STAGE}"

        return name

    # Docker Container 信息
    CONTAINER_WEB_LISTEN_PORT = 8000
    CONTAINER_WEB_BIND_ADDRESS = "0.0.0.0"
    CONTAINER_WEB_BIND_PORT = 8000

    def get_container_name(self, module: str) -> str:
        return f"{self.APP_NAME}-{self.DEPLOY_STAGE}-{module}"

    def switch_to_prd(self):
        pass

    def asdict(self) -> dict:
        return asdict(self)


ev = EnvValue()


@task
def deploy(c):
    conn = Connection(
        host=ev.DEPLOY_SSH_HOST, port=ev.DEPLOY_SSH_PORT, user=ev.DEPLOY_SSH_USER
    )

    docker_push_image(c)
    docker_pull_image(conn)

    run_restart_script(conn)

    _say_it("deploy finished")
