
import React, { useState, useEffect, memo } from "react";
import {
    ZoomableGroup,
    ComposableMap,
    Geographies,
    Geography,
    Sphere, Graticule
} from "react-simple-maps";
import { PatternLines } from "@vx/pattern";
import "react-tooltip/dist/react-tooltip.css";
import { Tooltip } from "react-tooltip";
import { geojson } from "./geo_data.js";
import { Container, Row, Form, Button, Col, ButtonGroup } from 'react-bootstrap';
import { scaleLinear } from "d3-scale";


const DateTimeForm = ({ updateDatesFunction, chosenDates }) => {
    const handleSubmit = (event) => {
        event.preventDefault();
        updateDatesFunction({ "date1": event.target.date1.value, "date2": event.target.date2.value });
    };

    return (
        <Form onSubmit={handleSubmit}>
            <Row className="align-items-end">
                <Col md={4}>
                    <Form.Group controlId="date1">
                        <Form.Label>Reference Date</Form.Label>
                        <Form.Control type="date"
                            defaultValue={chosenDates["date1"]}
                        />

                    </Form.Group>
                </Col>
                <Col md={4}>
                    <Form.Group controlId="date2">
                        <Form.Label>Compare Date</Form.Label>
                        <Form.Control type="date" defaultValue={chosenDates["date2"]} />
                    </Form.Group>
                </Col>
                <Col md={4} className="d-flex align-items-end justify-content-center">
                    <Button variant="primary" type="submit">
                        Submit
                    </Button>
                </Col>
            </Row>
        </Form>
    );
};
const MapChart = memo(({ setTooltipContent }) => {
    const defaultResult = {
        "data": {},
        "average": 0,
        "min": 0,
        "max": 0,
    }
    const [data, setData] = useState({
        "result1": defaultResult,
        "result2": defaultResult,
    });
    const get_current_date = () => new Date().toISOString().split("T")[0]
    const [dates, setDates] = useState({ "date1": get_current_date(), "date2": get_current_date() });
    const [isLoading, setIsLoading] = useState(true);
    useEffect(() => {
        const fetchData = async () => {
            try {
                setIsLoading(true);
                const response = await fetch(`/dns_data/first_date=${dates["date1"]}&second_date=${dates["date2"]}`);
                const jsonData = await response.json();
                setData(jsonData);
                console.log(jsonData)
                setIsLoading(false);
            } catch (error) {
                console.log(error.message)
            }
        };

        fetchData();
        console.log(dates)
    }, [dates]);
    // const choosenResult = "result2"



    const [choosenResult, setSelectedButton] = useState("result1");

    const handleButtonClick = (button) => {
        setSelectedButton(button);
    };
    const choosenData = data[`${choosenResult}`]
    const colorScale = scaleLinear()
        .domain([choosenData["min"], choosenData["average"], choosenData["max"]])
        .range(["green", "yellow", "red"]);
    return (
        <Container id="map"  >

            <Row>
                <ComposableMap style={{
                    width: '100%',
                    height: '75vh',
                    border: '1px solid black',
                    borderRadius: '10px'
                }}>
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
                                            const reference_result = data["result1"]["data"][`${geo.id}`] || "NA";
                                            const ref_string = `ref: \n${reference_result}${reference_result === "NA" ? "" : "ms"}`
                                            const compare_result = data["result2"]["data"][`${geo.id}`] || "NA";
                                            const cmp_string = `cmp: \n${compare_result}${compare_result === "NA" ? "" : "ms"}`
                                            setTooltipContent(`${name}: \n${ref_string}\n${cmp_string}`);
                                        }}
                                        onMouseLeave={() => {
                                            setTooltipContent("");
                                        }}
                                        stroke="#81a7e3"
                                        style={{
                                            default: {
                                                fill: choosenData["data"][`${geo.id}`] ? colorScale(choosenData["data"][`${geo.id}`]) : "url('#lines')",
                                                outline: "none"
                                            },
                                            hover: {
                                                fill: "#81a7e3",
                                                outline: "none"
                                            },
                                            pressed: {
                                                fill: "#E42",
                                                outline: "none"
                                            }
                                        }}
                                    />
                                ))
                            }
                        </Geographies>
                    </ZoomableGroup>
                </ComposableMap>
            </Row>
            {!isLoading ? (<Row className="mb-3">
                <Col>
                    <DateTimeForm updateDatesFunction={setDates} chosenDates={dates} />
                </Col>
            </Row>) : "Loading"}
            {!isLoading ? (<Row >
                <Col>
                    <ButtonGroup>
                        <Button
                            variant={choosenResult === 'result1' ? 'primary' : 'secondary'}
                            onClick={() => handleButtonClick('result1')}
                        >
                            Show Result of First Date
                        </Button>
                        <Button
                            variant={choosenResult === 'result2' ? 'primary' : 'secondary'}
                            onClick={() => handleButtonClick('result2')}
                        >
                            Show Result of Second Date
                        </Button>
                    </ButtonGroup>
                </Col>
            </Row>) : ""}
        </Container >
    );
});

function Graph() {
    const [content, setContent] = useState("");
    return (
        <div>
            <MapChart setTooltipContent={setContent} />
            <Tooltip anchorSelect="#map" content={content} float />
        </div>
    );
}

export default Graph;