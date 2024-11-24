FROM golang:1.23.3-bookworm

WORKDIR /app

COPY ./portfolio .

# Normal version
# RUN go install -v github.com/gohugoio/hugo@v0.139.0

# Extended version
RUN CGO_ENABLED=1 go install -tags extended github.com/gohugoio/hugo@v0.139.0

EXPOSE 1313
