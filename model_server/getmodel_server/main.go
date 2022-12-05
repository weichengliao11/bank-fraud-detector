package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"os"

	pb "getmodel"
	// 之後要把他放到github上...
	shell "github.com/ipfs/go-ipfs-api"
	"google.golang.org/grpc"
)

var (
	port       = flag.Int("port", 50052, "The server port")
	repo       = flag.String("repo", "/Users/yohowang/Desktop/四年級/下學期/分散式系統/ModelFetchingAndGrpc/grpc-go/examples/getmodel/repo", "Relative path where model stores")
	model_hash = flag.String("model_hash", "", "Newest model in ipfs")
	newest     = flag.String("newest", "m", "Newest model name")
)

type server struct {
	pb.UnimplementedGreeterServer
}

func (s *server) GetHash(ctx context.Context, in *pb.HashRequest) (*pb.HashReply, error) {
	reply, err := fetchModel()
	if err != nil {
		log.Fatalf("failed to get model: %v", err)
	}

	return &pb.HashReply{Hash: reply}, nil
}

func main() {
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterGreeterServer(s, &server{})
	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

func fetchModel() (string, error) {
	sh := shell.NewShell("localhost:5001")

	cid, err := sh.AddDir(*repo)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}

	content, err := sh.List(cid)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}

	for _, item := range content {
		if item.Name > *newest {
			*newest = item.Name
			*model_hash = item.Hash
		}
	}

	log.Printf("push %s and its hash %s", *newest, *model_hash)

	return *model_hash, nil
}
