/***************************************************************************
 *cr
 *cr            (C) Copyright 2007 The Board of Trustees of the
 *cr                        University of Illinois
 *cr                         All Rights Reserved
 *cr
 ***************************************************************************/
/*
 * GPU accelerated coulombic potential grid test code
 */

#include <CL/sycl.hpp>
#include <dpct/dpct.hpp>
#include <stdio.h>
#include <stdlib.h>
#include "WKFUtils.h"

/*
DPCT1010:0: SYCL uses exceptions to report errors and does not use the error
codes. The call was replaced with 0. You need to rewrite this code.
*/
/*
DPCT1009:1: SYCL uses exceptions to report errors and does not use the error
codes. The original code was commented out and a warning string was inserted.
You need to rewrite this code.
*/
#define CUERR                                                                  \
              { int err;                                                                 \
  if ((err = 0) != 0) {                                                      \
  printf("error: %s, line %d\n",                                               \
         "cudaGetErrorString not supported" /*cudaGetErrorString(err)*/,       \
         __LINE__);                                                            \
  return -1; }}

#define MAXATOMS 4000

#define UNROLLX       8
#define UNROLLY       1
#define BLOCKSIZEX    8
#define BLOCKSIZEY    8 
#define BLOCKSIZE    BLOCKSIZEX * BLOCKSIZEY

// This kernel calculates coulombic potential at each grid point and
// stores the results in the output array.
void cenergy(const int numatoms, const float gridspacing, float *energygrid,
             const sycl::float4 *atominfo, sycl::nd_item<3> item_ct1)
{
  unsigned int xindex = sycl::mul24((unsigned)item_ct1.get_group(2),
                                    (unsigned)item_ct1.get_local_range(2)) *
                            UNROLLX +
                        item_ct1.get_local_id(2);
  unsigned int yindex = sycl::mul24((unsigned)item_ct1.get_group(1),
                                    (unsigned)item_ct1.get_local_range(1)) +
                        item_ct1.get_local_id(1);
  unsigned int outaddr = (sycl::mul24((unsigned)item_ct1.get_group_range(2),
                                      (unsigned)item_ct1.get_local_range(2)) *
                          UNROLLX) *
                             yindex +
                         xindex;

  float coory = gridspacing * yindex;
  float coorx = gridspacing * xindex;

  float energyvalx1=0.0f;
  float energyvalx2=0.0f;
  float energyvalx3=0.0f;
  float energyvalx4=0.0f;
  float energyvalx5=0.0f;
  float energyvalx6=0.0f;
  float energyvalx7=0.0f;
  float energyvalx8=0.0f;

  float gridspacing_u = gridspacing * BLOCKSIZEX;

  //
  // XXX 59/8 FLOPS per atom
  //
  int atomid;
  for (atomid=0; atomid<numatoms; atomid++) {
    float dy = coory - atominfo[atomid].y();
    float dyz2 = (dy * dy) + atominfo[atomid].z();

    float dx1 = coorx - atominfo[atomid].x();
    float dx2 = dx1 + gridspacing_u;
    float dx3 = dx2 + gridspacing_u;
    float dx4 = dx3 + gridspacing_u;
    float dx5 = dx4 + gridspacing_u;
    float dx6 = dx5 + gridspacing_u;
    float dx7 = dx6 + gridspacing_u;
    float dx8 = dx7 + gridspacing_u;

    energyvalx1 += atominfo[atomid].w() * sycl::rsqrt(dx1 * dx1 + dyz2);
    energyvalx2 += atominfo[atomid].w() * sycl::rsqrt(dx2 * dx2 + dyz2);
    energyvalx3 += atominfo[atomid].w() * sycl::rsqrt(dx3 * dx3 + dyz2);
    energyvalx4 += atominfo[atomid].w() * sycl::rsqrt(dx4 * dx4 + dyz2);
    energyvalx5 += atominfo[atomid].w() * sycl::rsqrt(dx5 * dx5 + dyz2);
    energyvalx6 += atominfo[atomid].w() * sycl::rsqrt(dx6 * dx6 + dyz2);
    energyvalx7 += atominfo[atomid].w() * sycl::rsqrt(dx7 * dx7 + dyz2);
    energyvalx8 += atominfo[atomid].w() * sycl::rsqrt(dx8 * dx8 + dyz2);
  }

  energygrid[outaddr             ] += energyvalx1;
  energygrid[outaddr+1*BLOCKSIZEX] += energyvalx2;
  energygrid[outaddr+2*BLOCKSIZEX] += energyvalx3;
  energygrid[outaddr+3*BLOCKSIZEX] += energyvalx4;
  energygrid[outaddr+4*BLOCKSIZEX] += energyvalx5;
  energygrid[outaddr+5*BLOCKSIZEX] += energyvalx6;
  energygrid[outaddr+6*BLOCKSIZEX] += energyvalx7;
  energygrid[outaddr+7*BLOCKSIZEX] += energyvalx8;
}

int copyatoms(float *atoms, int count, float zplane, sycl::float4 *atominfo) {
  CUERR // check and clear any existing errors

  if (count > MAXATOMS) {
    printf("Atom count exceeds constant buffer storage capacity\n");
    return -1;
  }

  float atompre[4*MAXATOMS];
  int i;
  for (i=0; i<count*4; i+=4) {
    atompre[i    ] = atoms[i    ];
    atompre[i + 1] = atoms[i + 1];
    float dz = zplane - atoms[i + 2];
    atompre[i + 2]  = dz*dz;
    atompre[i + 3] = atoms[i + 3];
  }

  dpct::get_default_queue()
      .memcpy((float *)atominfo, atompre, count * 4 * sizeof(float))
      .wait();
  CUERR // check and clear any existing errors

  return 0;
}

int initatoms(float **atombuf, int count, sycl::range<3> volsize,
              float gridspacing) {
  sycl::float3 size;
  int i;
  float *atoms;
  srand(2);

  atoms = (float *) malloc(count * 4 * sizeof(float));
  *atombuf = atoms;

  // compute grid dimensions in angstroms
  size.x() = gridspacing * volsize[2];
  size.y() = gridspacing * volsize[1];
  size.z() = gridspacing * volsize[0];

  for (i=0; i<count; i++) {
    int addr = i * 4;
    atoms[addr] = (rand() / (float)RAND_MAX) * size.x();
    atoms[addr + 1] = (rand() / (float)RAND_MAX) * size.y();
    atoms[addr + 2] = (rand() / (float)RAND_MAX) * size.z();
    atoms[addr + 3] = ((rand() / (float) RAND_MAX) * 2.0) - 1.0;  // charge
  }  

  return 0;
}

int main(int argc, char **argv) {
  dpct::device_ext &dev_ct1 = dpct::get_current_device();
  sycl::queue &q_ct1 = dev_ct1.default_queue();
  float *doutput = NULL;
  sycl::float4 *datominfo = NULL;
  float *energy = NULL;
  float *atoms = NULL;
  sycl::range<3> volsize(1, 1, 1), Gsz(1, 1, 1), Bsz(1, 1, 1);
  wkf_timerhandle runtimer, mastertimer, copytimer, hostcopytimer;
  float copytotal, runtotal, mastertotal, hostcopytotal;
  const char *statestr = "|/-\\.";
  int state=0;

  printf("GPU accelerated coulombic potential microbenchmark\n");
  printf("--------------------------------------------------------\n");
  printf("  Single-threaded single-device test run.\n");

  // number of atoms to simulate
  int atomcount = 1000000;

  // setup energy grid size
  // XXX this is a large test case to clearly illustrate that even while
  //     the CUDA kernel is running entirely on the GPU, the CUDA runtime
  //     library is soaking up the entire host CPU for some reason.
  volsize[2] = 768;
  volsize[1] = 768;
  volsize[0] = 1;

  // set voxel spacing
  float gridspacing = 0.1;

  // setup CUDA grid and block sizes
  // XXX we have to make a trade-off between the number of threads per
  //     block and the resulting padding size we'll end up with since
  //     each thread will do several consecutive grid cells in this version,
  //     we're using up some of our available parallelism to reduce overhead.
  Bsz[2] = BLOCKSIZEX;
  Bsz[1] = BLOCKSIZEY;
  Bsz[0] = 1;
  Gsz[2] = volsize[2] / (Bsz[2] * UNROLLX);
  Gsz[1] = volsize[1] / (Bsz[1] * UNROLLY);
  Gsz[0] = volsize[0];

  // initialize the wall clock timers
  runtimer = wkf_timer_create();
  mastertimer = wkf_timer_create();
  copytimer = wkf_timer_create();
  hostcopytimer = wkf_timer_create();
  copytotal = 0;
  runtotal = 0;
  hostcopytotal = 0;

  printf("Grid size: %d x %d x %d\n", volsize[2], volsize[1], volsize[0]);
  printf("Running kernel(atoms:%d, gridspacing %g, z %d)\n", atomcount, gridspacing, 0);

  // allocate and initialize atom coordinates and charges
  if (initatoms(&atoms, atomcount, volsize, gridspacing))
    return -1;

  // allocate and initialize the GPU output array
  int volmemsz = sizeof(float) * volsize[2] * volsize[1] * volsize[0];
  printf("Allocating %.2fMB of memory for output buffer...\n", volmemsz / (1024.0 * 1024.0));

  doutput = (float *)sycl::malloc_device(volmemsz, q_ct1);
  datominfo = sycl::malloc_device<sycl::float4>(MAXATOMS, q_ct1);
  CUERR // check and clear any existing errors
      q_ct1.memset(doutput, 0, volmemsz)
          .wait();
  CUERR // check and clear any existing errors

  printf("starting run...\n");
  wkf_timer_start(mastertimer);

  int iterations=0;
  int atomstart;
  for (atomstart=0; atomstart<atomcount; atomstart+=MAXATOMS) {   
    iterations++;
    int runatoms;
    int atomsremaining = atomcount - atomstart;
    if (atomsremaining > MAXATOMS)
      runatoms = MAXATOMS;
    else
      runatoms = atomsremaining;

    printf("%c\r", statestr[state]);
    fflush(stdout);
    state = (state+1) & 3;

    // copy the atoms to the GPU
    wkf_timer_start(copytimer);
    if (copyatoms(atoms + 4*atomstart, runatoms, 0*gridspacing, datominfo)) 
      return -1;
    wkf_timer_stop(copytimer);
    copytotal += wkf_timer_time(copytimer);
 
    // RUN the kernel...
    wkf_timer_start(runtimer);
    /*
    DPCT1049:2: The workgroup size passed to the SYCL kernel may exceed the
    limit. To get the device limit, query info::device::max_work_group_size.
    Adjust the workgroup size if needed.
    */
    q_ct1.submit([&](sycl::handler &cgh) {
      cgh.parallel_for(sycl::nd_range<3>(Gsz * Bsz, Bsz),
                       [=](sycl::nd_item<3> item_ct1) {
                         cenergy(runatoms, 0.1, doutput, datominfo, item_ct1);
                       });
    });
    CUERR // check and clear any existing errors
    wkf_timer_stop(runtimer);
    runtotal += wkf_timer_time(runtimer);
  }
  dev_ct1.queues_wait_and_throw();
  printf("Done\n");

  wkf_timer_stop(mastertimer);
  mastertotal = wkf_timer_time(mastertimer);

  // Copy the GPU output data back to the host and use/store it..
  energy = (float *) malloc(volmemsz);
  wkf_timer_start(hostcopytimer);
  q_ct1.memcpy(energy, doutput, volmemsz).wait();
  CUERR // check and clear any existing errors
  wkf_timer_stop(hostcopytimer);
  hostcopytotal=wkf_timer_time(hostcopytimer);

  int i, j;
  for (j=0; j<8; j++) {
    for (i=0; i<8; i++) {
      int addr = j * volsize[2] + i;
      printf("[%d] %.1f ", addr, energy[addr]);
    }
    printf("\n");
  }

  printf("Final calculation required %d iterations of %d atoms\n", iterations, MAXATOMS);
  printf("Copy time: %f seconds, %f per iteration\n", copytotal, copytotal / (float) iterations);
  printf("Kernel time: %f seconds, %f per iteration\n", runtotal, runtotal / (float) iterations);
  printf("Total time: %f seconds\n", mastertotal);
  printf("Kernel invocation rate: %f iterations per second\n", iterations / mastertotal);
  printf("GPU to host copy bandwidth: %gMB/sec, %f seconds total\n",
         (volmemsz / (1024.0 * 1024.0)) / hostcopytotal, hostcopytotal);

  double atomevalssec =
      ((double)volsize[2] * volsize[1] * volsize[0] * atomcount) /
      (mastertotal * 1000000000.0);
  printf("Efficiency metric, %g billion atom evals per second\n", atomevalssec);

  /* 59/8 FLOPS per atom eval */
  printf("FP performance: %g GFLOPS\n", atomevalssec * (59.0/8.0));
  
  free(atoms);
  free(energy);
  sycl::free(doutput, q_ct1);
  sycl::free(datominfo, q_ct1);

  return 0;
}
