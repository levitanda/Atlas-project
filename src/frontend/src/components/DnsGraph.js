
import React, { useState, memo } from "react";
import {
    ZoomableGroup,
    ComposableMap,
    Geographies,
    Geography
} from "react-simple-maps";
import "react-tooltip/dist/react-tooltip.css";
import { Tooltip } from "react-tooltip";
import { geojson } from "./geo_data.js";
import Container from 'react-bootstrap/Container';

const MapChart = memo(({ setTooltipContent }) => {
    return (
        <Container id="map" >
            <ComposableMap style={{
                width: '100%',
                height: '90vh',
                border: '1px solid black'
            }}>
                <ZoomableGroup>
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
                                            fill: "#D6D6DA",
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
        </Container>
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
