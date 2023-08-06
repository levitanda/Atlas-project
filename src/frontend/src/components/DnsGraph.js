import React, { useState, useEffect, memo } from "react";
import {
  ZoomableGroup,
  ComposableMap,
  Geographies,
  Geography,
  Sphere,
  Graticule,
} from "react-simple-maps";
import { PatternLines } from "@vx/pattern";
import "react-tooltip/dist/react-tooltip.css";
import { Tooltip } from "react-tooltip";
import { geojson } from "./geo_data.js";
import {
  Container,
  Row,
  Form,
  Button,
  Col,
  ButtonGroup,
} from "react-bootstrap";
import { scaleLinear } from "d3-scale";
import {
  get_current_date,
  get_one_month_ago_from_today_date,
} from "./IpV6component.js";

const DateTimeForm = ({ updateDatesFunction, initialData }) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    updateDatesFunction({
      date1: event.target.date1.value,
      date2: event.target.date2.value,
    });
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Row className="d-flex align-items-end justify-content-center">
        <Col md={3}>
          <Form.Group controlId="date1">
            <Form.Label>Reference Date</Form.Label>
            <Form.Control type="date" defaultValue={initialData["date1"]} />
          </Form.Group>
        </Col>
        <Col md={3}>
          <Form.Group controlId="date2">
            <Form.Label>Compare Date</Form.Label>
            <Form.Control type="date" defaultValue={initialData["date2"]} />
          </Form.Group>
        </Col>
        <Col md={1}>
          <Button variant="primary" type="submit">
            Submit
          </Button>
        </Col>
      </Row>
    </Form>
  );
};

const DnsGraphController = memo(({ setTooltipContent }) => {
  const defaultResult = {
    data: {},
    average: 0,
    min: 0,
    max: 0,
  };
  const [data, setData] = useState({
    result1: defaultResult,
    result2: defaultResult,
  });
  const [dates, setDates] = useState({
    date1: get_one_month_ago_from_today_date(),
    date2: get_current_date(),
  });
  const [isLoading, setIsLoading] = useState(true);
  const [choosenResult, setSelectedButton] = useState("result1");

  const handleButtonClick = (button) => {
    setSelectedButton(button);
  };
  const choosenData = data[`${choosenResult}`];
  const [mode, changemode] = useState("whole_world");
  // const [mode, changemode] = useState("selected_countries");
  const renderContent = () => {
    if (mode == "whole_world") {
      return (
        <DnsCountryGraph
          data={data}
          setTooltipContent={setTooltipContent}
          choosenData={choosenData}
        />
      );
    } else if (mode == "selected_countries") {
      return (
        <Container
          style={{
            marginTop: "10px",
            height: "75vh",
            border: "1px solid black",
            borderRadius: "10px",
          }}
        />
      );
    }
  };
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(
          `/dns_data/first_date=${dates["date1"]}&second_date=${dates["date2"]}`
        );
        const jsonData = await response.json();
        setData(jsonData);
        setIsLoading(false);
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchData();
  }, [dates]);

  return (
    <Container id="map">
      <Row>{renderContent()}</Row>
      {!isLoading ? (
        <Row className="mb-3">
          <DateTimeForm updateDatesFunction={setDates} initialData={dates} />
        </Row>
      ) : (
        "Loading"
      )}
      {!isLoading ? (
        <Row>
          <Col>
            <ColorByDateChooser
              choosenResult={choosenResult}
              handleButtonClick={handleButtonClick}
            />
          </Col>
        </Row>
      ) : (
        ""
      )}
    </Container>
  );
});

const ColorByDateChooser = ({ choosenResult, handleButtonClick }) => {
  return (
    <ButtonGroup>
      <Button
        variant={choosenResult === "result1" ? "primary" : "secondary"}
        onClick={() => handleButtonClick("result1")}
      >
        Show Result of First Date
      </Button>
      <Button
        variant={choosenResult === "result2" ? "primary" : "secondary"}
        onClick={() => handleButtonClick("result2")}
      >
        Show Result of Second Date
      </Button>
    </ButtonGroup>
  );
};

function DnsCountryGraph({ data, setTooltipContent, choosenData }) {
  const colorScale = scaleLinear()
    .domain([choosenData["min"], choosenData["average"], choosenData["max"]])
    .range(["green", "yellow", "red"]);
  return (
    <ComposableMap
      style={{
        marginTop: "10px",
        height: "75vh",
        border: "1px solid black",
        borderRadius: "10px",
      }}
    >
      <PatternLines
        id="lines"
        height={6}
        width={6}
        stroke="#776865"
        strokeWidth={1}
        background="#F6F0E9"
        orientation={["diagonal"]}
      />
      <ZoomableGroup>
        <PatternLines
          id="lines"
          height={6}
          width={6}
          stroke="#776865"
          strokeWidth={1}
          background="#F6F0E9"
          orientation={["diagonal"]}
        />
        <Sphere stroke="#E4E5E6" strokeWidth={0.5} />
        <Graticule stroke="#E4E5E6" strokeWidth={0.5} />
        <Geographies geography={geojson}>
          {({ geographies }) =>
            geographies.map((geo) => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                onMouseEnter={() => {
                  const name = geo.properties.name;
                  const reference_result =
                    data["result1"]["data"][`${geo.id}`] || "NA";
                  const ref_string = `ref: \n${reference_result}${
                    reference_result === "NA" ? "" : "ms"
                  }`;
                  const compare_result =
                    data["result2"]["data"][`${geo.id}`] || "NA";
                  const cmp_string = `cmp: \n${compare_result}${
                    compare_result === "NA" ? "" : "ms"
                  }`;
                  setTooltipContent(`${name}: \n${ref_string}\n${cmp_string}`);
                }}
                onMouseLeave={() => {
                  setTooltipContent("");
                }}
                stroke="#81a7e3"
                style={{
                  default: {
                    fill: choosenData["data"][`${geo.id}`]
                      ? colorScale(choosenData["data"][`${geo.id}`])
                      : "url('#lines')",
                    outline: "none",
                  },
                  hover: {
                    fill: "#81a7e3",
                    outline: "none",
                  },
                  pressed: {
                    fill: "#E42",
                    outline: "none",
                  },
                }}
              />
            ))
          }
        </Geographies>
      </ZoomableGroup>
    </ComposableMap>
  );
}

function DnsGraphComponent() {
  const [content, setContent] = useState("");
  return (
    <React.Fragment>
      <DnsGraphController setTooltipContent={setContent} />
      <Tooltip anchorSelect="#map" content={content} float />
    </React.Fragment>
  );
}

export default DnsGraphComponent;
