package main

/*
bot.go
Copyright (c) 2019 Phil Hassey

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Galcon is a registered trademark of Phil Hassey
For more information see http://www.galcon.com/
*/

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
)

func send(msg string) { fmt.Println(msg) }
func log(msg string)  { fmt.Fprintln(os.Stderr, msg) }

////////////////////////////////////////////////////////////////////////////////

func bot(g *Galaxy) {
	var all, mine []*Item
	for _, o := range g.Items {
		if o.Type != PlanetType {
			continue
		}
		all = append(all, o)
		if o.Owner == g.You {
			mine = append(mine, o)
		}
	}
	if len(all) == 0 || len(mine) == 0 {
		return
	}
	source := mine[rand.Intn(len(mine))]
	target := all[rand.Intn(len(all))]
	send(fmt.Sprintf("/SEND %v %v %v\n", 5*(1+rand.Intn(20)), source.N, target.N))
}

////////////////////////////////////////////////////////////////////////////////

type ID = int
type Number = float64
type Type = uint8
type Color = uint32

func toNumber(v string) Number {
	n, _ := strconv.ParseFloat(v, 64)
	return Number(n)
}

func toID(v string) ID {
	n, _ := strconv.ParseInt(v, 10, 64)
	return ID(n)
}

func toColor(v string) Color {
	n, _ := strconv.ParseInt(v, 16, 64)
	return Color(n)
}

const (
	TeamType = Type(iota)
	UserType
	PlanetType
	FleetType
	UnitType
	NeutralTeam = ID(0)
)

type Item struct {
	N          ID
	Type       Type
	X          Number
	Y          Number
	Radius     Number
	Source     ID
	Target     ID
	Production Number
	Ships      Number
	Name       string
	Team       ID
	Owner      ID
	Color      Color
}

type Galaxy struct {
	Items map[ID]*Item
	You   ID
	State string
}

func NewGalaxy() *Galaxy {
	return &Galaxy{
		Items: make(map[ID]*Item),
	}
}

func main() {
	g := NewGalaxy()
	r := bufio.NewReader(os.Stdin)
	for {
		line, _, err := r.ReadLine()
		if err != nil {
			break
		}
		if len(line) == 0 {
			continue
		}
		parse(g, string(line))
	}
}

func parse(g *Galaxy, line string) {
	t := strings.Split(line, "\t")
	if t[0][0] != '/' {
		sync(g, t)
		return
	}
	switch t[0] {
	case "/TICK":
		bot(g)
		send("/TOCK")
	case "/PRINT":
		log(strings.Join(t[1:], "\t"))
	case "/RESULTS":
		log(strings.Join(t[1:], "\t"))
	case "/RESET":
		*g = *NewGalaxy()
	case "/SET":
		switch t[1] {
		case "YOU":
			g.You = toID(t[2])
		case "STATE":
			g.State = t[2]
		}
	case "/USER":
		n := toID(t[1])
		g.Items[n] = &Item{
			N:     n,
			Type:  UserType,
			Name:  t[2],
			Color: toColor(t[3]),
			Team:  toID(t[4]),
		}
	case "/PLANET":
		n := toID(t[1])
		g.Items[n] = &Item{
			N:          n,
			Type:       PlanetType,
			Owner:      toID(t[2]),
			Ships:      toNumber(t[3]),
			X:          toNumber(t[4]),
			Y:          toNumber(t[5]),
			Production: toNumber(t[6]),
			Radius:     toNumber(t[7]),
		}
	case "/FLEET":
		n := toID(t[1])
		g.Items[n] = &Item{
			N:      n,
			Type:   FleetType,
			Owner:  toID(t[2]),
			Ships:  toNumber(t[3]),
			X:      toNumber(t[4]),
			Y:      toNumber(t[5]),
			Source: toID(t[6]),
			Target: toID(t[7]),
			Radius: toNumber(t[8]),
		}
	case "/DESTROY":
		delete(g.Items, toID(t[1]))
	case "/ERROR":
		log(strings.Join(t[1:], "\t"))
	default:
		log("unhandled command: " + strings.Join(t, "\t"))
	}
}

func sync(g *Galaxy, t []string) {
	nFields, fields := len(t[0]), strings.ToUpper(t[0])
	i := 1
	for i < len(t) {
		n := toID(t[i])
		i++
		if o, ok := g.Items[n]; ok {
			for _, k := range fields {
				v := t[i]
				i++
				switch k {
				case 'X':
					o.X = toNumber(v)
				case 'Y':
					o.Y = toNumber(v)
				case 'S':
					o.Ships = toNumber(v)
				case 'R':
					o.Radius = toNumber(v)
				case 'O':
					o.Owner = toID(v)
				case 'T':
					o.Target = toID(v)
				}
			}
		} else {
			i += nFields
		}
	}
}
