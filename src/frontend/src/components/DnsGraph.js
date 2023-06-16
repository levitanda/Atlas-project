
import React, { useState, useEffect, memo } from "react";
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

function getRandomFloat(min, max) {
    return Math.random() * (max - min) + min;
}
const DateTimeForm = ({ updateDatesFunction, chosenDates }) => {
    const handleSubmit = (event) => {
        event.preventDefault();
        const data = new FormData(event.target);
        const [date1, date2] = [data.get('date'), data.get('date2')];
        updateDatesFunction({ "date1": date1, "date2": date2 });
    };

    return (
        <Form onSubmit={handleSubmit}>
            <Row className="align-items-end">
                <Col md={4}>
                    <Form.Group controlId="date1">
                        <Form.Label>Start Date</Form.Label>
                        <Form.Control type="date" value={chosenDates["date1"]} />
                    </Form.Group>
                </Col>
                <Col md={4}>
                    <Form.Group controlId="date2">
                        <Form.Label>End Date</Form.Label>
                        <Form.Control type="date" value={chosenDates["date2"]} />
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
const specific_data = {
    'ALB': 31.782400000000003,
    'AND': 21.443,
    'ARE': 26.734,
    'ARG': 92.34663725490198,
    'ARM': 66.24,
    'AUS': 36.16388055555555,
    'AUT': 24.646471230158735,
    'AZE': 76.688,
    'BEL': 25.33087736318408,
    'BGD': 53.399,
    'BGR': 47.82113802083332,
    'BIH': 25.56,
    'BLM': 244.483,
    'BLR': 41.388157894736835,
    'BOL': 91.2305,
    'BRA': 44.25674747474747,
    'BRB': 50.868,
    'BWA': 57.36,
    'CAN': 38.961641393442626,
    'CHE': 19.03115598290598,
    'CHL': 98.24932870370372,
    'CHN': 127.12836231884057,
    'COL': 82.81433333333334,
    'CZE': 19.25544666666666,
    'DEU': 24.982163308144397,
    'DJI': 79.119,
    'DNK': 23.079567610062895,
    'DOM': 27.296999999999997,
    'ECU': 96.8995,
    'ESP': 68.1416755319149,
    'EST': 42.888371527777785,
    'FIN': 42.80792592592593,
    'FRA': 24.844370433789955,
    'GBR': 23.258286802030455,
    'GEO': 67.287,
    'GHA': 182.47899999999998,
    'GLP': 81.096,
    'GRC': 44.19012765957447,
    'HKG': 13.923440476190475,
    'HRV': 23.024032608695656,
    'HUN': 43.48086451612904,
    'IDN': 72.13343055555556,
    'IMN': 47.262,
    'IND': 101.99913265306125,
    'IRL': 19.674161375661374,
    'IRN': 158.47064000000003,
    'IRQ': 11.131,
    'ISL': 98.092,
    'ISR': 63.36144444444446,
    'ITA': 29.337314536340855,
    'JOR': 70.34700000000001,
    'JPN': 49.15126666666665,
    'KAZ': 94.318625,
    'KOR': 66.31271666666667,
    'KWT': 19.674,
    'LBN': 28.2775,
    'LIE': 13.51136666666667,
    'LKA': 42.551,
    'LTU': 31.429756944444446,
    'LUX': 24.068857142857137,
    'LVA': 54.53320555555556,
    'MDA': 15.390666666666666,
    'MDG': 257.131,
    'MEX': 51.409015151515156,
    'MLT': 31.809,
    'MYS': 62.051470588235304,
    'NAM': 42.194,
    'NLD': 12.73082781456953,
    'NOR': 50.04989186046513,
    'NZL': 111.93546774193548,
    'PER': 106.94745833333334,
    'PHL': 72.53128571428572,
    'POL': 21.748104377104383,
    'PRT': 46.3295502136752,
    'PYF': 99.079,
    'REU': 72.6712,
    'ROU': 36.789049621212115,
    'RUS': 62.52573691460052,
    'SAU': 79.07425,
    'SGP': 67.07735,
    'SRB': 35.888999999999996,
    'SVK': 24.457107843137255,
    'SVN': 21.696976666666668,
    'SWE': 25.092354166666663,
    'THA': 66.33515555555556,
    'TTO': 50.828,
    'TUN': 66.438,
    'TUR': 48.66532608695652,
    'TWN': 33.992,
    'TZA': 78.371875,
    'UKR': 52.09366120218581,
    'URY': 39.921,
    'USA': 42.29142289719629,
    'UZB': 78.88,
    'VEN': 89.43599999999999,
    'VNM': 91.11080000000001,
    'YEM': 221.837,
    'ZAF': 88.57708080808082,
    'ZMB': 21.629,
    'ZWE': 18.315
}

const MapChart = memo(({ setTooltipContent }) => {
    const colorScale = scaleLinear()
        .domain([11.131, 257.131])
        .range(["#ffedea", "#ff5233"]);
    const [data, setData] = useState([]);
    const get_current_date = () => new Date().toISOString().split("T")[0]
    const [dates, setDates] = useState({ "date1": get_current_date(), "date2": get_current_date() });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`/dns_data/first_date=${dates["date1"]}&second_date=${dates["date2"]}`);
                const jsonData = await response.json();
                setData(specific_data);
                console.log(jsonData)
            } catch (error) {
                console.log(error.message)
            }
        };

        fetchData();
        console.log(dates)
    }, [dates]);

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
                                            setTooltipContent(`${geo.properties.name}:${specific_data[`${geo.id}`] || "NA"}`);
                                        }}
                                        onMouseLeave={() => {
                                            setTooltipContent("");
                                        }}
                                        style={{
                                            default: {
                                                // fill: "#D6D6DA",
                                                fill: colorScale(
                                                    specific_data[`${geo.id}`] || 0
                                                ),
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
                    <DateTimeForm updateDatesFunction={setDates} chosenDates={dates} />
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
            <Tooltip anchorSelect="#map" content={content} float />
        </div>
    );
}

export default Graph;
