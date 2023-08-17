import React, { useState, useMemo, useEffect } from "react";
import {
  //LineChart,
  //Line,
  //XAxis,
  //YAxis,
  //CartesianGrid,
  //Tooltip,
  //Legend,
  //ResponsiveContainer,
} from "recharts";
import { Container, Row, Form, Button, Col, Spinner } from "react-bootstrap";
import countryList from "react-select-country-list";
import {
  LineChartGraphBody,
  DatesCountryForm,
} from "./DnsGraph.js";
import { geojson } from "./geo_data.js";

export const get_current_date = () => new Date().toISOString().split("T")[0];
export const get_n_days_ago_from_current_date = (n) => {
  let date = new Date();
  date.setDate(date.getDate() - n);
  return date.toISOString().split("T")[0];
};
export const get_n_days_ago_from_given_date = (date, n) => {
  // date in the format of YYYY-MM-DD
  let date_obj = new Date(date);
  date_obj.setDate(date_obj.getDate() - n);
  return date_obj.toISOString().split("T")[0];
};

const IpV6Controller = () => {
  const geo_options = useMemo(
    () =>
      geojson.objects.world.geometries.map((item) => {
        return { value: item.id, label: item.properties.name };
      }),
    []
  );
  const [state, setState] = useState({
    data: [],
    startDate: get_n_days_ago_from_given_date(get_current_date(), 2),
    endDate: get_current_date(),
    countries: [geo_options.find((item) => item.value == "ISR")],
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
        console.log("real loading")
        //TODO: check if I can use state.countries this way!
        const first_date = state.startDate;
        const second_date = state.endDate;
        console.log(first_date, second_date)
        const jsonCountries = JSON.stringify(state.countries);
        const response = await fetch(
            `/ipv/country=${jsonCountries}&first_date=${first_date}&second_date=${second_date}`
        );
        const jsonData = await response.json();
        console.log(jsonData)
        setIsLoadingState(false);
        updateData(jsonData.data);
      } catch (error) {
        console.log(error.message);
      }
    };
    fetchData();
  }, [state.startDate, state.endDate, state.countries]);
  return (
    <Container>
      {!state.isLoading ? (
        <React.Fragment>
          <Row>
            <LineChartGraphBody
              state={state}
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

export function LoadingSpinner() {
  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{ height: "75vh" }}
    >
      <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  );
}
const IpV6component = () => {
  return <IpV6Controller />;
};

export default IpV6component;
