import { useState } from 'react';
import Tab from 'react-bootstrap/Tab';
import Stack from 'react-bootstrap/Stack';
import Tabs from 'react-bootstrap/Tabs';
import Graph from "./DnsGraph";

function ControlledTabsExample() {
    const [key, setKey] = useState('DNS');

    return (
        <Tabs
            id="controlled-tab-example"
            activeKey={key}
            onSelect={(k) => setKey(k)}
        // className="mb-3"
        >
            <Tab eventKey="DNS" title="DNS availability">
                <Graph />
            </Tab>
            <Tab eventKey="IPv6" title="IPv6 deployment">
                <Stack gap={3}>
                    <div className="bg-warning border">First item</div>
                    <div className="bg-warning border">Second item</div>
                    <div className="bg-warning border">Third item</div>
                </Stack>
            </Tab>
        </Tabs>
    );
}

export default ControlledTabsExample;