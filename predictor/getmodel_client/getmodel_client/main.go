package main

import (
	"context"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"time"

	pb "getmodel"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	shell "github.com/ipfs/go-ipfs-api"
)

var (
	addr = flag.String("addr", "localhost:50052", "the address to connect to")
)

func main() {
	flag.Parse()
	conn, err := grpc.Dial(*addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()

	c := pb.NewGreeterClient(conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	r, err := c.GetHash(ctx, &pb.HashRequest{})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}

	sh := shell.NewShell("localhost:5001")
	new_version, err := sh.Cat(r.Hash)

	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}
	defer new_version.Close()

	body, err := ioutil.ReadAll(new_version)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}

	origin := string(body)

	if _, err := os.Stat("./model.sav"); err == nil {
		err = os.Remove("./model.sav")
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %s", err)
			os.Exit(1)
		}
	}

	f, err := os.Create("./model.sav")
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}
	defer f.Close()

	_, err = f.WriteString(origin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s", err)
		os.Exit(1)
	}

	fmt.Println("Clone done.")
}
