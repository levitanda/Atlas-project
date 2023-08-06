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
import { get_current_date } from "./IpV6component.js";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const DateTimeForm = ({ updateDatesFunction, defaultDate }) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    updateDatesFunction(event.target.date1.value);
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Row className="d-flex align-items-end justify-content-center">
        <Col md={3}>
          <Form.Group controlId="date1">
            <Form.Label>Date</Form.Label>
            <Form.Control type="date" defaultValue={defaultDate} />
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

const DnsGraphController = memo(
  ({ setTooltipContent, changeMode, setCountryCode, setCountryChartDate }) => {
    const defaultResult = {
      data: {},
      average: 0,
      min: 0,
      max: 0,
    };
    const [data, setData] = useState(defaultResult);
    const [date, setDate] = useState(get_current_date());
    const upddateDate = (newDate) => {
      setDate(newDate);
      setCountryChartDate(newDate);
    };

    const [isLoading, setIsLoading] = useState(true);
    useEffect(() => {
      const fetchData = async () => {
        try {
          setIsLoading(true);
          const response = await fetch(`/dns_data/${date}`);
          const jsonData = await response.json();
          setData(jsonData);
          setIsLoading(false);
        } catch (error) {
          console.log(error.message);
        }
      };
      fetchData();
    }, [date]);

    return (
      <Container id="map">
        <Row>
          <DnsCountryGraph
            data={data}
            setTooltipContent={setTooltipContent}
            changeModeHandler={changeMode}
            changeCountryCodeHandler={setCountryCode}
          />
        </Row>
        {!isLoading ? (
          <Row className="mb-3">
            <DateTimeForm
              updateDatesFunction={upddateDate}
              defaultDate={date}
            />
          </Row>
        ) : (
          "Loading"
        )}
      </Container>
    );
  }
);

const DnsCountyLineChart = ({ initial_country_code, initial_date }) => {
  const [state, setState] = useState({
    data: [],
    isLoading: true,
    startDate: "2020-01-02",
    endDate: "2020-01-03",
    countries: [initial_country_code],
  });
  const setIsLoadingState = (loadingState) => {
    setState({ ...state, isLoading: loadingState });
  };
  const updateData = (newData) => {
    setState({ ...state, data: newData });
  };
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoadingState(true);
        const response = await fetch(
          `/dns_data_line/${state.startDate}/${state.endDate}/`
        );
        const jsonData = await response.json();
        console.log(jsonData.data);
        setIsLoadingState(false);
        updateData(jsonData.data);
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchData();
  }, [state.startDate, state.endDate]);
  return (
    <Container
      style={{
        marginTop: "10px",
        height: "75vh",
        border: "1px solid black",
        borderRadius: "10px",
      }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={state.data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <ChartTooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey={state.countries[0]}
            stroke="#8884d8"
            activeDot={{ r: 8 }}
          />
          {/* <Line type="monotone" dataKey="uv" stroke="#82ca9d" /> */}
        </LineChart>
      </ResponsiveContainer>
    </Container>
  );
};
function DnsCountryGraph({
  data,
  setTooltipContent,
  changeModeHandler,
  changeCountryCodeHandler,
}) {
  const colorScale = scaleLinear()
    .domain([data["min"], data["average"], data["max"]])
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
                  const dns_result = data["data"][`${geo.id}`] || "NA";
                  const dns_result_with_unit =
                    dns_result != "NA" ? `${dns_result} ms` : dns_result;
                  setTooltipContent(`${name}: \n${dns_result_with_unit}`);
                }}
                onClick={() => {
                  changeCountryCodeHandler(geo.id);
                  changeModeHandler("selected_countries");
                  setTooltipContent("");
                }}
                onMouseLeave={() => {
                  setTooltipContent("");
                }}
                stroke="#81a7e3"
                style={{
                  default: {
                    fill: data["data"][`${geo.id}`]
                      ? colorScale(data["data"][`${geo.id}`])
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

function DnsGraphComponent({ changeMode, selectCountry, setCountryChartDate }) {
  const [tooltip_content, setTooltipContent] = useState("");
  return (
    <React.Fragment>
      <DnsGraphController
        setTooltipContent={setTooltipContent}
        changeMode={changeMode}
        setCountryCode={selectCountry}
        setCountryChartDate={setCountryChartDate}
      />
      <Tooltip anchorSelect="#map" content={tooltip_content} float />
    </React.Fragment>
  );
}
const DnsPageController = () => {
  const [mode, changeMode] = useState("whole_world");
  const [country_code, setCountryCode] = useState("");
  const [country_chart_date, setCountryChartDate] = useState(
    get_current_date()
  );
  const renderContent = () => {
    if (mode == "whole_world") {
      return (
        <DnsGraphComponent
          changeMode={changeMode}
          selectCountry={setCountryCode}
          setCountryChartDate={setCountryChartDate}
        />
      );
    } else if (mode == "selected_countries") {
      return (
        <DnsCountyLineChart
          initial_country_code={country_code}
          initial_date={country_chart_date}
        />
      );
    }
  };
  return renderContent();
};

export default DnsPageController;
