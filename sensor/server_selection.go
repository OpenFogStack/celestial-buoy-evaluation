package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"
)

func selectHostAPI(apiEndpoint string, id string) string {
	url := fmt.Sprintf("http://%s/gst/%s", apiEndpoint, id)
	resp, err := http.Get(url)
	if err != nil {
		log.Printf("couldn't get %s: %s", url, err.Error())
		return ""
	}

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Printf("couldn't read response body: %s", err.Error())
		return ""
	}

	// what we got was not a json!
	// continue
	if !strings.HasPrefix(string(body), "{") {
		log.Printf("got response: %s (not a json)\n", string(body))
		return ""
	}

	type Sat struct {
		Sat   int
		Shell int
	}

	type SatInfo struct {
		Sat   Sat
		Delay float64
	}

	type Info struct {
		ConnectedSats []SatInfo
	}

	i := Info{}

	err = json.Unmarshal(body, &i)
	if err != nil {
		log.Printf("couldn't unmarshal body (%s): %s", string(body), err.Error())
		return ""
	}

	resp.Body.Close()

	if len(i.ConnectedSats) == 0 {
		log.Printf("no connected satellites (body %s)", string(body))
		return ""
	}

	best := i.ConnectedSats[0]
	for _, sat := range i.ConnectedSats {
		if sat.Delay < best.Delay {
			best = sat
		}
	}

	log.Printf("best satellite %d %d selected from %s %+v\n", best.Sat.Sat, best.Sat.Shell, string(body), i.ConnectedSats)

	return fmt.Sprintf("%d.%d.celestial", best.Sat.Sat, best.Sat.Shell)
}

func informDataGenEndpoint(endpoint string, host string) error {
	_, err := http.PostForm(fmt.Sprintf("http://%s", endpoint), url.Values{"server": {host}})

	return err
}

func main() {
	// service selects the optimal server to send the request to
	// can be a static host (ground station) or based on connection to satellites

	selectionMethod := flag.String("method", "satellite", "satellite or groundstation")
	staticHost := flag.String("host", "", "host to use if method is groundstation")
	dataGenEndpoint := flag.String("data-gen-endpoint", "", "endpoint to inform about the selected host")
	apiEndpoint := flag.String("api-endpoint", "", "celestial api endpoint")
	flag.Parse()

	var identifier string
	var curr string

	// try to send the host to data_gen service once and then exit
	if *selectionMethod == "groundstation" {
		for {
			time.Sleep(5 * time.Second)
			err := informDataGenEndpoint(*dataGenEndpoint, *staticHost)
			if err != nil {
				log.Printf("couldn't inform data_gen endpoint: %s", err.Error())
				continue
			}
			return
		}
	}

	for {
		time.Sleep(3 * time.Second)
		url := fmt.Sprintf("http://%s/self", *apiEndpoint)

		resp, err := http.Get(url)
		if err != nil {
			log.Println("couldn't get url", err.Error())
			continue
		}

		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Println("couldn't read body", err.Error())
			continue
		}

		resp.Body.Close()

		// what we got was not a json!
		// continue
		if !strings.HasPrefix(string(body), "{") {
			log.Printf("got response: %s (waiting)\n", string(body))
			continue
		}

		id := struct {
			Name string
		}{}
		err = json.Unmarshal(body, &id)
		if err != nil {
			fmt.Println("couldn't parse json", err.Error(), string(body))
			continue
		}

		identifier = id.Name

		if identifier == "" {
			log.Println("couldn't get identifier from api endpoint")
			continue
		}

		log.Println("identifier:", identifier)
		break
	}

	for {
		time.Sleep(10 * time.Second)
		log.Println("selecting host")
		best := selectHostAPI(*apiEndpoint, identifier)

		// if the one with the best performance is not the current one, switch to it
		if best == curr || best == "" {
			time.Sleep(10 * time.Second)
			log.Println("no new best host")
			continue
		}

		log.Println("found new best host:", best)
		// send to data_gen endpoint
		err := informDataGenEndpoint(*dataGenEndpoint, best)

		if err != nil {
			log.Println("couldn't inform data gen endpoint", err.Error())
			continue
		}

		curr = best
	}
}
