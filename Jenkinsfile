def appname = "hello-newapp"
def repo = "yuval597"
def appimage = "docker.io/${repo}/${appname}"
def apptag = "${env.BUILD_NUMBER}"

podTemplate(cloud: 'kubernetes', containers: [
    containerTemplate(
        name: 'jnlp',
        image: 'jenkins/inbound-agent:latest'
    ),
    containerTemplate(
        name: 'docker',
        image: 'docker:26-dind',
        privileged: true,
        args: '--storage-driver=vfs'
    )
],
volumes: [
    emptyDirVolume(mountPath: '/var/lib/docker', memory: false)
]) {
    node(POD_LABEL) {

        stage('checkout') {
            container('jnlp') {
                sh '/usr/bin/git config --global http.sslVerify false'
                checkout scm
            }
        }

        stage('Build') {
            container('docker') {
                echo "Building docker image..."
                sh "docker build -t $appimage:$apptag ."
            }
        }

        stage('Push') {
            container('docker') {
                withCredentials([usernamePassword(
                    credentialsId: 'dockercred',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    echo "Logging to DockerHub"
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'

                    echo "Pushing docker"
                    sh "docker push $appimage:$apptag"
                }
            }
        }
    }
}
