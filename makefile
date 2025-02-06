.PHONY: clean up

clean:
	docker stop `docker ps -a -q`
	docker rm `docker ps -a -q`
	# docker rmi `docker images -q`

up:
	docker compose up --build

postgres_shell:
	docker exec -it `docker ps --filter "name=postgres" -q` psql -h localhost -p 5432 -U postgres -d users_service -W

mongo_shell:
	docker exec -it `docker ps --filter "name=mongo" -q` mongos