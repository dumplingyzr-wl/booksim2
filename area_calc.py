import math

PD_UTILIZATION = 0.7
WIRE_DENSITY = 0.00008
SRAM_DENSITY = 0.15
FF_DENSITY = 0.458
VC_ALLOC_COEF = 1.2
SW_ALLOC_COEF = 1.2
XBAR_COEF = 1.2

REQ_HDR_WIDTH = 118
RSP_HDR_WIDTH = 69
REQ_PLD_WIDTH = 293
RSP_PLD_WIDTH = 261
CREDIT_WIDTH = 8


def area_calc(
    k,
    use_sram,
    internal_speedup,
    buffer_policy,
    num_vc,
    buffer_size_per_vc,
    shared_buffer_size,
    req_channel_width,
    rsp_channel_width,
):
    buffer_entry_total = 0
    linked_list_size = 0
    buffer_unit_area = SRAM_DENSITY
    if use_sram == False:
        buffer_unit_area = FF_DENSITY
    if buffer_policy == "private":
        buffer_entry_total = num_vc * buffer_size_per_vc * k
    else:
        buffer_entry_total = (num_vc * buffer_size_per_vc + shared_buffer_size) * k
        linked_list_size = buffer_entry_total * math.log2(buffer_entry_total / k) * 2

    buffer_area = (
        buffer_entry_total * (req_channel_width + rsp_channel_width) * buffer_unit_area
        + linked_list_size * FF_DENSITY
    )
    vc_alloc_area = (
        num_vc
        * k
        * (req_channel_width + rsp_channel_width)
        * FF_DENSITY
        * VC_ALLOC_COEF
    )
    sw_alloc_area = (
        internal_speedup
        * k
        * (req_channel_width + rsp_channel_width)
        * FF_DENSITY
        * SW_ALLOC_COEF
    )
    xbar_area = (
        internal_speedup
        * k
        * (req_channel_width + rsp_channel_width)
        * FF_DENSITY
        * XBAR_COEF
    )
    logic_area = (
        buffer_area + vc_alloc_area + sw_alloc_area + xbar_area
    ) / PD_UTILIZATION

    return logic_area


if __name__ == "__main__":
    serialize_header_body = False
    use_sram = True
    k = 4
    n = 3
    buffer_policy = "private"
    internal_speedup = 1
    num_vc = 8
    buffer_size_per_vc = 8
    shared_buffer_size = 32

    f = open("area_sweep.csv", "w")
    f.write(
        "ser_header, use_sram, buff_policy, i_spd_up, num_vc, buff_size_private, buff_size_shared, area(mm^2), bounding_factor\n"
    )

    req_channel_width = max(REQ_HDR_WIDTH, REQ_PLD_WIDTH) + CREDIT_WIDTH
    rsp_channel_width = max(RSP_HDR_WIDTH, RSP_PLD_WIDTH) + CREDIT_WIDTH

    port_count = math.pow(k, n)
    instance_cnt = port_count / k * n

    for serialize_header_body in [True, False]:
        if not serialize_header_body:
            req_channel_width = REQ_HDR_WIDTH + REQ_PLD_WIDTH + CREDIT_WIDTH
            rsp_channel_width = RSP_HDR_WIDTH + RSP_PLD_WIDTH + CREDIT_WIDTH
        io_area = math.pow(
            (port_count / 2 * (req_channel_width + rsp_channel_width) * WIRE_DENSITY), 2
        )
        for use_sram in [True, False]:
            for buffer_policy in ["private", "shared"]:
                for internal_speedup in [1, 2]:
                    for num_vc in [2, 4, 8]:
                        if buffer_policy == "private":
                            for buffer_size_per_vc in [2, 4, 8, 16]:
                                inst_area = area_calc(
                                    k,
                                    use_sram,
                                    internal_speedup,
                                    buffer_policy,
                                    num_vc,
                                    buffer_size_per_vc,
                                    shared_buffer_size,
                                    req_channel_width,
                                    rsp_channel_width,
                                )
                                area = inst_area * instance_cnt / 1000000
                                io_bounded = io_area > area
                                bounding_factor = "IO" if io_bounded else "logic"
                                line = [
                                    str(serialize_header_body),
                                    str(use_sram),
                                    buffer_policy,
                                    str(internal_speedup),
                                    str(num_vc),
                                    str(buffer_size_per_vc),
                                    str(shared_buffer_size),
                                    str("{:.3f}".format(max(area, io_area))),
                                    bounding_factor,
                                ]
                                f.write(",".join(line) + "\n")
                        else:
                            for buffer_size_per_vc in [2, 4, 8]:
                                for shared_buffer_size in [8, 16, 32]:
                                    inst_area = area_calc(
                                        k,
                                        use_sram,
                                        internal_speedup,
                                        buffer_policy,
                                        num_vc,
                                        buffer_size_per_vc,
                                        shared_buffer_size,
                                        req_channel_width,
                                        rsp_channel_width,
                                    )
                                    area = inst_area * instance_cnt / 1000000
                                    io_bounded = io_area > area
                                    bounding_factor = "IO" if io_bounded else "logic"
                                    line = [
                                        str(serialize_header_body),
                                        str(use_sram),
                                        buffer_policy,
                                        str(internal_speedup),
                                        str(num_vc),
                                        str(buffer_size_per_vc),
                                        str(shared_buffer_size),
                                        str("{:.3f}".format(max(area, io_area))),
                                        bounding_factor,
                                    ]
                                    f.write(",".join(line) + "\n")

    # print("Area per router instance: %.3f mm^2" % (area))
    # print("Instance count: ", instance_cnt)
    # print("Total area: %.3f mm^2" % (area))
    # print("Total IO area: %.3f mm^2" % (io_area))
    # print("Bounding factor: ", bounding_factor)
