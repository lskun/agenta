import {useCallback} from "react"

import {Button, Typography} from "antd"
import clsx from "clsx"

import usePlayground from "@/components/NewPlayground/hooks/usePlayground"

import {useStyles} from "./styles"
import RunButton from "../../../../assets/RunButton"
import {clearRuns} from "../../../../hooks/usePlayground/assets/generationHelpers"
import TestsetDrawerButton from "../../../Drawers/TestsetDrawer"
import LoadTestsetButton from "../../../Modals/LoadTestsetModal/assets/LoadTestsetButton"

import type {PlaygroundStateData} from "../../../../hooks/usePlayground/types"
import type {GenerationHeaderProps} from "./types"

const GenerationHeader = ({variantId}: GenerationHeaderProps) => {
    const classes = useStyles()
    const {results, isRunning, mutate, runTests} = usePlayground({
        variantId,
        stateSelector: useCallback(
            (state: PlaygroundStateData) => {
                const inputRows = state.generationData.inputs.value

                const results = inputRows.map((inputRow) =>
                    variantId ? inputRow?.__runs?.[variantId]?.__result : null,
                )

                const isRunning = inputRows.some((inputRow) =>
                    variantId ? inputRow?.__runs?.[variantId]?.__isRunning : false,
                )

                return {results, isRunning}
            },
            [variantId],
        ),
    })

    const clearGeneration = useCallback(() => {
        mutate(
            (clonedState) => {
                if (!clonedState) return clonedState
                clearRuns(clonedState)
                return clonedState
            },
            {revalidate: false},
        )
    }, [mutate])

    return (
        <section
            className={clsx("h-[48px] flex justify-between items-center gap-4", classes.container)}
        >
            <Typography className="text-[16px] leading-[18px] font-[600] text-nowrap">
                Generations
            </Typography>

            <div className="flex items-center gap-2">
                <Button size="small" onClick={clearGeneration} disabled={isRunning}>
                    Clear
                </Button>

                <LoadTestsetButton label="Load Test set" />

                <TestsetDrawerButton
                    label="Add all to test set"
                    icon={false}
                    size="small"
                    disabled={isRunning}
                    results={results}
                />

                <RunButton
                    isRunAll
                    type="primary"
                    onClick={() => runTests?.()}
                    disabled={isRunning}
                />
            </div>
        </section>
    )
}

export default GenerationHeader
