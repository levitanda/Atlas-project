
import React, { useState, memo } from "react";
import {
    ZoomableGroup,
    ComposableMap,
    Geographies,
    Geography,
    Sphere, Graticule
} from "react-simple-maps";
import "react-tooltip/dist/react-tooltip.css";
import { Tooltip } from "react-tooltip";
import { geojson } from "./geo_data.js";
import { Container, Row, Form, Button, Col } from 'react-bootstrap';
import { scaleLinear } from "d3-scale";
const colorScale = scaleLinear()
    .domain([0.29, 0.68])
    .range(["#ffedea", "#ff5233"]);
function getRandomFloat(min, max) {
    return Math.random() * (max - min) + min;
}
const DateTimeForm = () => {
    const handleSubmit = (event) => {
        event.preventDefault();
        // Handle form submission
    };

    return (
        <Form onSubmit={handleSubmit}>
            <Row className="align-items-end">
                <Col md={4}>
                    <Form.Group controlId="date">
                        <Form.Label>Start Date</Form.Label>
                        <Form.Control type="date" />
                    </Form.Group>
                </Col>
                <Col md={4}>
                    <Form.Group controlId="date2">
                        <Form.Label>End Date</Form.Label>
                        <Form.Control type="date" />
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
    const [data, setData] = useState([]);

    return (
        <Container id="map"  >
            <Row>
                <ComposableMap style={{
                    width: '100%',
                    height: '85vh',
                    border: '1px solid black',
                    borderRadius: '10px'
                }}>
                    <ZoomableGroup>
                        <Sphere stroke="#E4E5E6" strokeWidth={0.5} />
                        <Graticule stroke="#E4E5E6" strokeWidth={0.5} />
                        <Geographies geography={geojson}>
                            {({ geographies }) =>
                                geographies.map((geo) => (
                                    <Geography
                                        key={geo.rsmKey}
                                        geography={geo}
                                        onMouseEnter={() => {
                                            setTooltipContent(`${geo.properties.name}`);
                                        }}
                                        onMouseLeave={() => {
                                            setTooltipContent("");
                                        }}
                                        style={{
                                            default: {
                                                // fill: "#D6D6DA",
                                                fill: colorScale(getRandomFloat(0.29, 0.68)),
                                                outline: "none"
                                            },
                                            hover: {
                                                fill: "#F53",
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
            <Row>
                <Col>
                    <DateTimeForm />
                </Col>
            </Row>
        </Container >
    );
});

function Graph() {
    const [content, setContent] = useState("");
    return (
        <div>
            <MapChart setTooltipContent={setContent} />
            <Tooltip anchorId="map" content={content} float />
        </div>
    );
}

export default Graph;
