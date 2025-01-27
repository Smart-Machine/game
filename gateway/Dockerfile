# Build Stage
FROM golang:1.23-alpine as builder

RUN apk add --no-cache git

WORKDIR /app

COPY . .

RUN go mod tidy 

RUN go build -o gateway .

# Final Stage
FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/gateway /app/gateway

EXPOSE 8080

CMD ["./gateway"]
