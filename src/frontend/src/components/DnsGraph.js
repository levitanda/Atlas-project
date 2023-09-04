import React, { useState, useEffect, useMemo, memo } from "react";
import { interpolateRgb } from "d3-interpolate";
import {
  ZoomableGroup,
  ComposableMap,
  Geographies,
  Geography,
  Sphere,
  Graticule,
} from "react-simple-maps";
import { PatternLines } from "@visx/pattern";
import "react-tooltip/dist/react-tooltip.css";
import { Tooltip } from "react-tooltip";
import { geojson } from "./geo_data.js";
import { Container, Row, Form, Button, Col } from "react-bootstrap";
import { scaleLinear } from "d3-scale";
import {
  LoadingSpinner,
  get_current_date,
  get_n_days_ago_from_given_date,
} from "./IpV6component.js";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  Label,
  ResponsiveContainer,
  Brush,
} from "recharts";
import Select from "react-select";

const DateChooseForm = ({ updateDatesFunction, defaultDate }) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    updateDatesFunction(event.target.date.value);
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Row className="d-flex align-items-end justify-content-center">
        <Col md={3}>
          <Form.Group controlId="date">
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
  ({
    setTooltipContent,
    changeMode,
    setCountryCode,
    setCountryChartDate,
    countryChartDate,
  }) => {
    const defaultResult = {
      data: {},
      average: 0,
      min: 0,
      max: 0,
    };
    const [data, setData] = useState(defaultResult);
    const [date, setDate] = useState(countryChartDate);
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
          <Row>
            <DateChooseForm
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

const DnsCountryLineChartController = ({
  initial_country_code,
  initial_date,
  changeMode,
  setCountryChartDate,
}) => {
  const geo_options = useMemo(
    () =>
      geojson.objects.world.geometries.map((item) => {
        return { value: item.id, label: item.properties.name };
      }),
    []
  );

  const [state, setState] = useState({
    data: [],
    startDate: get_n_days_ago_from_given_date(initial_date, 2),
    endDate: initial_date,
    // startDate: "2019-09-01",
    // endDate: "2020-07-01",
    // endDate: "2021-07-01",
    countries: [geo_options.find((item) => item.value == initial_country_code)],
  });
  const setIsLoadingState = (loadingState) => {
    setState({ ...state, isLoading: loadingState });
  };
  const updateData = (newData) => {
    setState({ ...state, data: newData });
  };
  const updateSelectedCountries = (newCountries) => {
    setState({ ...state, countries: newCountries });
  };
  const updateDates = (newStartDate, newEndDate) => {
    setState({ ...state, startDate: newStartDate, endDate: newEndDate });
  };
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoadingState(true);
        const response = await fetch(
          `/dns_data_line/${state.startDate}/${state.endDate}/`
        );
        const jsonData = await response.json();
        setIsLoadingState(false);
        updateData(jsonData.data);
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchData();
  }, [state.startDate, state.endDate]);
  return (
    <Container>
      {!state.isLoading ? (
        <React.Fragment>
          <Row>
            <LineChartGraphBody
              state={state}
              changeMode={changeMode}
              setCountryChartDate={setCountryChartDate}
              units={"DNS response time (ms)"}
            />
          </Row>
          <DatesCountryForm
            updateDates={updateDates}
            updateSelectedCountries={updateSelectedCountries}
            state={state}
            geo_options={geo_options}
          />
        </React.Fragment>
      ) : (
        <LoadingSpinner />
      )}
    </Container>
  );
};

export function LineChartGraphBody({
  state,
  changeMode = (item) => {},
  setCountryChartDate = (item) => {},
  units = "IP v6 percentage ",
}) {
  const colorScale = scaleLinear()
    .domain([0, state.countries.length])
    .range(["red", "blue"])
    .interpolate(interpolateRgb);

  // Generate n contrast colors
  const colors = Array.from({ length: state.countries.length }, (_, i) =>
    colorScale(i)
  );
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
          <YAxis label={{ value: units, angle: -90, position: "insideLeft" }} />

          <ChartTooltip />
          <Legend />
          {state.countries.map((country, index) => (
            <Line
              key={country.value}
              type="monotone"
              dataKey={country.value}
              stroke={colors[index]}
              activeDot={{
                r: 8,
                onClick: (event, payload) => {
                  setCountryChartDate(payload.payload["name"]);
                  changeMode("whole_world");
                },
              }}
            />
          ))}
          <Brush />
        </LineChart>
      </ResponsiveContainer>
    </Container>
  );
}

export function DatesCountryForm({
  updateDates,
  updateSelectedCountries,
  state,
  geo_options,
}) {
  return (
    <Form
      onSubmit={(event) => {
        event.preventDefault();
        const date1 = new Date(event.target.start_date.value);
        const date2 = new Date(event.target.end_date.value);
        const today = new Date();

        // set the hours, minutes, seconds and milliseconds to 0 to compare only the date part
        today.setHours(0, 0, 0, 0);
        date1.setHours(0, 0, 0, 0);
        date2.setHours(0, 0, 0, 0);

        if (date1 > today || date2 > today) {
          alert("Selected dates cannot be in the future!");
          return;
        }
        if (date1 > date2) {
          alert("Start date cannot be after end date!");
          return;
        }

        updateDates(event.target.start_date.value, event.target.end_date.value);
      }}
    >
      <Row className="d-flex align-items-end justify-content-center">
        <Form.Group as={Col} md={3} controlId="country">
          <Form.Label>Country</Form.Label>
          <Select
            isMulti
            styles={{
              menuList: (provided, state) => ({
                ...provided,
                maxHeight: "80px",
              }),
            }}
            onChange={(selected) => {
              updateSelectedCountries(selected);
            }}
            value={state.countries}
            options={geo_options}
            // isDisabled={}
          />
        </Form.Group>
        <Form.Group as={Col} md={3} controlId="start_date">
          <Form.Label>Start Date</Form.Label>
          <Form.Control defaultValue={state.startDate} type="date" />
        </Form.Group>
        <Form.Group as={Col} md={3} controlId="end_date">
          <Form.Label>End Date</Form.Label>
          <Form.Control defaultValue={state.endDate} type="date" />
        </Form.Group>
        <Col md={1}>
          <Button variant="primary" type="submit">
            Submit
          </Button>
        </Col>
      </Row>
    </Form>
  );
}

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
                    dns_result !== "NA" ? `${dns_result} ms` : dns_result;
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

function DnsGraphComponent({
  changeMode,
  selectCountry,
  setCountryChartDate,
  countryChartDate,
}) {
  const [tooltip_content, setTooltipContent] = useState("");
  return (
    <React.Fragment>
      <DnsGraphController
        setTooltipContent={setTooltipContent}
        changeMode={changeMode}
        setCountryCode={selectCountry}
        setCountryChartDate={setCountryChartDate}
        countryChartDate={countryChartDate}
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
    if (mode === "whole_world") {
      return (
        <DnsGraphComponent
          changeMode={changeMode}
          selectCountry={setCountryCode}
          setCountryChartDate={setCountryChartDate}
          countryChartDate={country_chart_date}
        />
      );
    } else if (mode === "selected_countries") {
      return (
        <DnsCountryLineChartController
          initial_country_code={country_code}
          setCountryChartDate={setCountryChartDate}
          initial_date={country_chart_date}
          changeMode={changeMode}
        />
      );
    }
  };
  return renderContent();
};

export default DnsPageController;
