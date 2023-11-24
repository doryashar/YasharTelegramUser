## TODO:
- use telegram bot file id instead of downloading the file: https://github.com/LonamiWebs/Telethon/issues/1613
- fix main python, docker, and docker-compose files to support running each agent.
- each agent should be using a base class with producer and consumer and config loader
- wrap each agent with failure recovery mechanism.
- program kafka to leave only 1 day of messages.
- add photo/document/audio/album messages.
- each processor should subscribe to broadcast.
- add duplicate removal to the processor.
- rate limit each broadcaster -> add signal mechanism?
- monitor the instances. 

<!-- ## To run:
docker build -t yasharnews .
docker run yasharnews -->



