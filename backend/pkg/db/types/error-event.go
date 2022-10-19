package types

import (
	"encoding/hex"
	"encoding/json"
	"hash/fnv"
	"log"
	"strconv"

	. "openreplay/backend/pkg/messages"
)

type ErrorEvent struct {
	MessageID uint64
	Timestamp uint64
	Source    string
	Name      string
	Message   string
	Payload   string
	Tags      map[string]*string
}

func unquote(s string) string {
	if s[0] == '"' {
		return s[1 : len(s)-1]
	}
	return s
}
func parseTags(tagsJSON string) (tags map[string]*string, err error) {
	if tagsJSON[0] == '[' {
		var tagsArr []json.RawMessage
		if err = json.Unmarshal([]byte(tagsJSON), &tagsArr); err != nil {
			return
		}

		tags = make(map[string]*string)
		for _, keyBts := range tagsArr {
			tags[unquote(string(keyBts))] = nil
		}
	} else if tagsJSON[0] == '{' {
		var tagsObj map[string]json.RawMessage
		if err = json.Unmarshal([]byte(tagsJSON), &tagsObj); err != nil {
			return
		}

		tags = make(map[string]*string)
		for key, valBts := range tagsObj {
			val := unquote(string(valBts))
			tags[key] = &val
		}
	}
	return
}

func WrapJSException(m *JSException) *ErrorEvent {
	meta, err := parseTags(m.Metadata)
	if err != nil {
		log.Printf("Error on parsing Exception metadata: %v", err)
	}
	return &ErrorEvent{
		MessageID: m.Meta().Index,
		Timestamp: uint64(m.Meta().Timestamp),
		Source:    "js_exception",
		Name:      m.Name,
		Message:   m.Message,
		Payload:   m.Payload,
		Tags:      meta,
	}
}

func WrapIntegrationEvent(m *IntegrationEvent) *ErrorEvent {
	return &ErrorEvent{
		MessageID: m.Meta().Index, // This will be always 0 here since it's coming from backend TODO: find another way to index
		Timestamp: m.Timestamp,
		Source:    m.Source,
		Name:      m.Name,
		Message:   m.Message,
		Payload:   m.Payload,
	}
}

func (e *ErrorEvent) ID(projectID uint32) string {
	hash := fnv.New128a()
	hash.Write([]byte(e.Source))
	hash.Write([]byte(e.Name))
	hash.Write([]byte(e.Message))
	hash.Write([]byte(e.Payload))
	return strconv.FormatUint(uint64(projectID), 16) + hex.EncodeToString(hash.Sum(nil))
}
