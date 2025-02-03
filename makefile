.PHONY: clean up

clean:
	docker stop `docker ps -a -q`
	docker rm `docker ps -a -q`
	# docker rmi `docker images -q`

up:
	docker compose up --build